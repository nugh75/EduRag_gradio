import torch
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import  EMBEDDING_CONFIG
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import EMBEDDING_CONFIG, EMBEDDING_MODEL
def get_embeddings():

    """Inizializza gli embeddings usando il modello configurato"""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_CONFIG["model_name"],
        model_kwargs={'device': device}
    )
def create_chunks(text):
    from app.config import EMBEDDING_CONFIG
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=EMBEDDING_CONFIG["chunk_size"],
        chunk_overlap=EMBEDDING_CONFIG["chunk_overlap"],
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_text(text)


def create_vectorstore(texts, metadatas, db_path):
    embeddings = get_embeddings()
    db = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
   


