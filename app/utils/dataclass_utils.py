import os
import json
from dataclasses import dataclass
from app.utils.database_handling import BASE_DB_PATH

@dataclass
class DocumentMetadata:
    """
    Classe per gestire i metadati dei documenti.
    
    Attributi:
        filename (str): Nome del file originale
        title (str): Titolo assegnato al documento
        author (str): Autore del documento
        upload_date (str): Data di caricamento
        chunks (int): Numero di chunks in cui è stato diviso il documento
    """
    filename: str
    title: str
    author: str
    upload_date: str
    chunks: int
    
    def to_dict(self):
        """Converte i metadati in un dizionario per il salvataggio JSON."""
        return {
            "filename": self.filename,
            "title": self.title,
            "author": self.author,
            "upload_date": self.upload_date,
            "chunks": self.chunks
        }

def save_metadata(metadata_list, db_name):
    """
    Salva i metadati dei documenti nel database specificato.
    
    Args:
        metadata_list: Lista di oggetti DocumentMetadata da salvare
        db_name: Nome del database in cui salvare i metadati
        
    Note:
        I metadati vengono salvati in un file JSON nella directory del database
    """
    db_path = os.path.join(BASE_DB_PATH, f"faiss_index_{db_name}")
    metadata_file = os.path.join(db_path, "metadata.json")
    
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    
    existing_metadata = []
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            existing_metadata = json.load(f)
    
    existing_metadata.extend([m.to_dict() for m in metadata_list])
    
    with open(metadata_file, 'w') as f:
        json.dump(existing_metadata, f, indent=2)
