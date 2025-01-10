import logging
from langchain_community.vectorstores import FAISS
import os
import json
from datetime import datetime
from app.utils.database_handling import BASE_DB_PATH
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.utils.embedding_utils import *
from app.utils.dataclass_utils import DocumentMetadata, save_metadata
from app.utils.extract_utils import extract_text_from_pdf, extract_text_from_docx


# -------------- DOCUMENT MANAGEMENT TAB FUNCTIONS --------------

def merge_metadata(existing_metadata, new_metadata, db_name):
    """Unisce i metadati esistenti con i nuovi."""
    metadata_path = os.path.join(BASE_DB_PATH, f"faiss_index_{db_name}", "metadata.json")
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            existing_metadata = json.load(f)
    else:
        existing_metadata = []
    
    # Converte i nuovi metadati in dizionari
    new_metadata_dicts = [meta.to_dict() if hasattr(meta, 'to_dict') else meta for meta in new_metadata]
    existing_metadata.extend(new_metadata_dicts)
    
    return existing_metadata

def upload_and_index(files, title, author, db_name="default_db"):
    if not files:
        return False, "Nessun file caricato.", ""
        
    documents = []
    doc_metadata = []
    
    # Crea directory del database se non esiste
    db_path = os.path.join(BASE_DB_PATH, f"faiss_index_{db_name}")
    os.makedirs(db_path, exist_ok=True)
    
    embeddings = get_embeddings()
    existing_vectorstore = None
    current_chunk_offset = 0
    
    try:
        # Calcola l'ultimo ID chunk utilizzato
        last_chunk_id = 0
        if os.path.exists(os.path.join(db_path, "metadata.json")):
            with open(os.path.join(db_path, "metadata.json"), 'r') as f:
                existing_metadata = json.load(f)
                last_chunk_id = sum(doc['chunks'] for doc in existing_metadata)
    
        if os.path.exists(os.path.join(db_path, "index.faiss")):
            existing_vectorstore = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        logging.error(f"Errore caricamento vectorstore esistente: {e}")
        existing_vectorstore = None
        last_chunk_id = 0
    
    # Processa i nuovi file
    for file in files:
        try:
            if file.name.endswith('.pdf'):
                text = extract_text_from_pdf(file.name)
            elif file.name.endswith('.docx'):
                text = extract_text_from_docx(file.name)
            else:
                with open(file.name, 'r', encoding='utf-8') as f:
                    text = f.read()
                    
            chunks = create_chunks(text)
            
            doc_meta = DocumentMetadata(
                filename=os.path.basename(file.name),
                title=title,
                author=author,
                upload_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                chunks=len(chunks)
            )
            doc_metadata.append(doc_meta)
            
            # Aggiungi metadati a ogni chunk
            for i, chunk in enumerate(chunks):
                chunk_id = last_chunk_id + i
                chunk_metadata = {
                    "content": chunk,
                    "source": os.path.basename(file.name),
                    "title": title,
                    "author": author,
                    "chunk_id": chunk_id,  # ID univoco del chunk
                    "doc_chunk_index": i,  # Indice del chunk nel documento
                    "total_doc_chunks": len(chunks),
                    "filename": os.path.basename(file.name)  # Aggiunto per riferimento
                }
                documents.append(chunk_metadata)
            
            last_chunk_id += len(chunks)
            
        except Exception as e:
            logging.error(f"Errore durante la lettura del file {file.name}: {e}")
            continue

    if documents:
        try:
            texts = [doc["content"] for doc in documents]
            metadatas = [{k: v for k, v in doc.items() if k != "content"} for doc in documents]
            
            if existing_vectorstore:
                existing_vectorstore.add_texts(texts, metadatas=metadatas)
                vectorstore = existing_vectorstore
            else:
                vectorstore = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
            
            vectorstore.save_local(db_path)
            
            # Aggiorna metadata.json
            final_metadata = merge_metadata([], doc_metadata, db_name)
            with open(os.path.join(db_path, "metadata.json"), 'w') as f:
                json.dump(final_metadata, f, indent=2)
            
            return True, "Documenti indicizzati con successo!", f"Database '{db_name}' aggiornato"
            
        except Exception as e:
            error_msg = f"Errore durante l'indicizzazione: {e}"
            logging.error(error_msg)
            return False, error_msg, ""
    
    return False, "Nessun documento processato.", ""

def list_indexed_files(db_name="default_db"):
    db_path = os.path.join(BASE_DB_PATH, f"faiss_index_{db_name}")  # Modifica qui
    metadata_file = os.path.join(db_path, "metadata.json")
    
    if not os.path.exists(metadata_file):
        return "Nessun file nel database."
    
    try:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        if not metadata:
            return "Nessun documento nel database."
        
        output = []
        for doc in metadata:
            output.append(
                f"📄 {doc['title']}\n"
                f"   Autore: {doc['author']}\n"
                f"   File: {doc['filename']}\n"
                f"   Chunks: {doc['chunks']}\n"
                f"   Caricato il: {doc['upload_date']}\n"
            )
        
        return "\n".join(output) if output else "Nessun documento nel database."
    except Exception as e:
        logging.error(f"Errore nella lettura dei metadati: {e}")
        return f"Errore nella lettura dei metadati: {e}"

def delete_file_from_database(file_name, db_name="default_db"):
    """Elimina un file e i suoi chunks dal database."""
    db_path = os.path.join(BASE_DB_PATH, f"faiss_index_{db_name}")
    metadata_path = os.path.join(db_path, "metadata.json")
    
    if not os.path.exists(metadata_path):
        return "Database non trovato (metadata.json mancante)."
    
    try:
        # Carica i metadati esistenti
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Trova il file da eliminare
        file_index = next((i for i, doc in enumerate(metadata) 
                          if doc['filename'] == file_name), -1)
        
        if file_index == -1:
            return f"File '{file_name}' non trovato nel database."
            
        # Carica il vectorstore esistente
        embeddings = get_embeddings()
        vectorstore = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        
        # Calcola l'intervallo di chunks da rimuovere
        chunks_before = sum(doc['chunks'] for doc in metadata[:file_index])
        chunks_to_remove = metadata[file_index]['chunks']
        
        # Estrai tutti i documenti tranne quelli da rimuovere
        all_docs = list(vectorstore.docstore._dict.items())
        docs_to_keep = (
            all_docs[:chunks_before] + 
            all_docs[chunks_before + chunks_to_remove:]
        )
        
        # Rimuovi il file dai metadati
        metadata.pop(file_index)
        
        # Ricrea il vectorstore da zero
        if docs_to_keep:
            texts = [doc[1].page_content for doc in docs_to_keep]
            metadatas = [doc[1].metadata for doc in docs_to_keep]
            new_vectorstore = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
            new_vectorstore.save_local(db_path)
        else:
            # Se non ci sono più documenti, rimuovi il vectorstore
            os.remove(os.path.join(db_path, "index.faiss"))
            os.remove(os.path.join(db_path, "index.pkl"))
        
        # Salva i metadati aggiornati
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        return f"File '{file_name}' eliminato con successo."
        
    except Exception as e:
        logging.error(f"Errore durante l'eliminazione: {e}")
        return f"Errore durante l'eliminazione: {e}"


