# llm_handling.py
import logging
import os
from langchain_community.vectorstores import FAISS
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import json
from collections import defaultdict

from app.config import (
    BASE_DB_PATH,
    LLM_CONFIGS, 
    LLMType,
    EMBEDDING_CONFIG,
    LLM_CONFIGS_EXTENDED
)
from app.configs.prompts import SYSTEM_PROMPTS
from app.utils.embedding_utils import get_embeddings


logging.basicConfig(level=logging.INFO)

# =====================================
# Functions related to LLM
# =====================================

def get_llm_client(llm_type: LLMType):
    """Obtains the appropriate client for the selected model"""
    config = LLM_CONFIGS.get(llm_type)
    if not config:
        raise ValueError(f"Model {llm_type} not supported")
    
    if llm_type == LLMType.ANTHROPIC:
        from langchain_anthropic import ChatAnthropic
        model = config["model"]
        client = ChatAnthropic(model_name=model, anthropic_api_key="my-api-key")
        return client, model
    
    client_class = config["client"]
    model = config["model"]
    client = client_class()  # Ensure no arguments are needed
    return client, model

def get_system_prompt(prompt_type="tutor"):
    """Selects the appropriate system prompt"""
    return SYSTEM_PROMPTS.get(prompt_type, SYSTEM_PROMPTS["tutor"])

def test_local_connection():
    """Checks connection to the local LLM server"""
    try:
        response = requests.get(f"http://192.168.43.199:1234/v1/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def read_metadata(db_path):
    metadata_file = os.path.join(db_path, "metadata.json")
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return []

def get_relevant_documents(vectorstore, question):
    """Retrieves relevant documents from the vectorstore based on similarity threshold"""
    try:
        enhanced_query = enhance_query(question)
        # Get all documents with their similarity scores
        docs_and_scores = vectorstore.similarity_search_with_score(enhanced_query)
        # Filter documents based on similarity threshold
        filtered_docs = [
            doc for doc, score in docs_and_scores 
            if score >= EMBEDDING_CONFIG['min_similarity']
        ]
        logging.info(f"Query: {question}")
        logging.info(f"Documents found: {len(filtered_docs)}")
        return filtered_docs if filtered_docs else []
    except Exception as e:
        logging.error(f"Error retrieving documents: {e}")
        return []

def enhance_query(question):
    stop_words = set(['il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una'])
    words = [w for w in question.lower().split() if w not in stop_words]
    return " ".join(words)

def log_search_results(question, docs_and_scores):
    logging.info(f"Query: {question}")
    for idx, (doc, score) in enumerate(docs_and_scores, 1):
        logging.info(f"Doc {idx} - Score: {score:.4f}")
        logging.info(f"Content: {doc.page_content[:100]}...")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def summarize_context(messages):
    """Crea un riassunto del contesto mantenendo le informazioni chiave"""
    summary = []
    key_info = set()
    
    for msg in messages:
        if msg["role"] == "system":
            continue
            
        # Estrai informazioni chiave
        content = msg["content"]
        if "fonte" in content.lower() or "fonti" in content.lower():
            key_info.add(content)
        elif "importante" in content.lower() or "nota" in content.lower():
            key_info.add(content)
            
    if key_info:
        summary.append({
            "role": "system",
            "content": "Contesto riassunto:\n" + "\n".join(f"- {info}" for info in key_info)
        })
        
    return summary

def answer_question(question, db_name, prompt_type="tutor", chat_history=None, llm_type=LLMType.OPENAI_GPT_4O_MINI):
    if chat_history is None:
        chat_history = []
        
    # Configurazione dinamica della cronologia
    MAX_HISTORY_TOKENS = int(LLM_CONFIGS_EXTENDED["max_tokens"] * 0.4)  # 40% dei token totali
    MIN_HISTORY_ITEMS = 2  # Mantieni almeno l'ultimo scambio
    
    # Calcola la lunghezza della cronologia attuale
    current_tokens = sum(len(m["content"].split()) for m in chat_history)
    
    # Se superiamo il limite, creiamo un riassunto
    if current_tokens > MAX_HISTORY_TOKENS:
        summary = summarize_context(chat_history)
        # Manteniamo l'ultimo scambio completo
        last_exchange = chat_history[-MIN_HISTORY_ITEMS:]
        chat_history = summary + last_exchange
    
    try:
        # Setup e recupero documenti
        db_path = os.path.join(BASE_DB_PATH, f"faiss_index_{db_name}")
        embeddings = get_embeddings()
        vectorstore = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        relevant_docs = get_relevant_documents(vectorstore, question)
        
        if not relevant_docs:
            return [
                {"role": "user", "content": question},
                {"role": "assistant", "content": "Mi dispiace, non ho trovato informazioni rilevanti."}
            ]

        # Leggi metadata.json per il totale dei chunks
        metadata_path = os.path.join("db", f"faiss_index_{db_name}", "metadata.json")
        with open(metadata_path, 'r') as f:
            metadata_list = json.load(f)
        
        # Crea dizionario titolo -> chunks
        total_chunks = {doc['title']: doc['chunks'] for doc in metadata_list}
        
        # Prepara le fonti
        sources = []
        for doc in relevant_docs:
            meta = doc.metadata
            title = meta.get('title', 'Unknown')
            author = meta.get('author', 'Unknown')
            filename = meta.get('filename', 'Unknown')
            chunk_id = meta.get('chunk_id', 0)  # Usa l'ID univoco del chunk
            total_doc_chunks = total_chunks.get(title, 0)
            
            # Usa lo stesso formato di chunks_viewer_tab.py
            chunk_info = f"📚 Chunk {chunk_id} - {title} ({filename})"
            if author != 'Unknown':
                chunk_info += f" - Author: {author}"
            
            sources.append(chunk_info)

        # Prepara contesto e prompt
        context = "\n".join([doc.page_content for doc in relevant_docs])
        sources_text = "\n\nFonti consultate:\n" + "\n".join(set(sources))
        prompt = SYSTEM_PROMPTS[prompt_type].format(context=context)
        prompt += "\nCita sempre le fonti utilizzate nella risposta, inclusi titolo e autore."

        # Crea messaggio e ottieni risposta
        messages = [
            {"role": "system", "content": prompt},
            *[{"role": m["role"], "content": m["content"]} for m in chat_history],
            {"role": "user", "content": question}
        ]
        
        client, model = get_llm_client(llm_type)
        if llm_type == LLMType.ANTHROPIC:
            response = client(messages)
            answer = response.content + sources_text
        else:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature= LLM_CONFIGS_EXTENDED["temperature"],
                max_tokens=LLM_CONFIGS_EXTENDED["max_tokens"]
            )
            answer = response.choices[0].message.content + sources_text
        return [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer}
        ]
    except Exception as e:
        logging.error(f"Error in answer_question: {e}")
        error_msg = "LLM locale non disponibile." if "local" in str(llm_type) else str(e)
        return [
            {"role": "user", "content": question},
            {"role": "assistant", "content": f"⚠️ {error_msg}"}
        ]

class DocumentRetriever:
    def __init__(self, db_path):
        self.embeddings = get_embeddings()
        self.vectorstore = FAISS.load_local(
            db_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
    def get_relevant_chunks(self, question):
        enhanced_query = enhance_query(question)
        docs_and_scores = self.vectorstore.similarity_search_with_score(enhanced_query)
        log_search_results(question, docs_and_scores)
        return [
            doc for doc, score in docs_and_scores
            if score >= EMBEDDING_CONFIG['min_similarity']
        ]

if __name__ == "__main__":
    pass
