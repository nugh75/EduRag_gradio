import logging
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.config import BASE_DB_PATH

# Crea la cartella db se non esiste
if not os.path.exists(BASE_DB_PATH):
    os.makedirs(BASE_DB_PATH)

# -------------- DATABASE MANAGEMENT TAB FUNCTIONS --------------
def create_database(db_name):
    logging.info(f"Creating database: {db_name}")
    db_path = os.path.join(BASE_DB_PATH, f"faiss_index_{db_name}")

    if os.path.exists(db_path):
        return f"Il database '{db_name}' esiste già."

    try:
        os.makedirs(db_path)
        logging.info(f"Database {db_name} created successfully.")
        return f"Database '{db_name}' creato con successo."
    except Exception as e:
        logging.error(f"Errore nella creazione del database: {e}")
        return f"Errore nella creazione del database: {e}"

def delete_database(db_name):
    db_path = os.path.join(BASE_DB_PATH, f"faiss_index_{db_name}")
    if not os.path.exists(db_path):
        return f"Il database '{db_name}' non esiste."
    try:
        shutil.rmtree(db_path)
        logging.info(f"Database {db_name} eliminato con successo.")
        return f"Database '{db_name}' eliminato con successo."
    except OSError as e:
        logging.error(f"Impossibile eliminare il database {db_name}: {e}")
        return f"Impossibile eliminare il database '{db_name}': {e}"

def modify_database(old_db_name, new_db_name):
    old_db_path = os.path.join(BASE_DB_PATH, f"faiss_index_{old_db_name}")
    new_db_path = os.path.join(BASE_DB_PATH, f"faiss_index_{new_db_name}")
    if not os.path.exists(old_db_path):
        return f"Il database '{old_db_name}' non esiste."
    if os.path.exists(new_db_path):
        return f"Il database '{new_db_name}' esiste già."
    try:
        os.rename(old_db_path, new_db_path)
        return f"Database '{old_db_name}' rinominato in '{new_db_name}' con successo."
    except Exception as e:
        return f"Errore durante la modifica del database: {e}"

def list_databases():
    try:
        databases = []
        for item in os.listdir(BASE_DB_PATH):
            if os.path.isdir(os.path.join(BASE_DB_PATH, item)) and item.startswith("faiss_index_"):
                db_name = item.replace("faiss_index_", "")
                databases.append(db_name)
        # Ensure "default_db" is in the list
        if "default_db" not in databases:
            databases.append("default_db")
        return databases
    except Exception as e:
        logging.error(f"Error listing databases: {e}")
        return []

class DatabaseChangeHandler(FileSystemEventHandler):
    """Handler per monitorare i cambiamenti nella cartella db."""
    def __init__(self, update_callback):
        self.update_callback = update_callback

    def on_any_event(self, event):
        if event.is_directory:  # Monitora solo le directory
            self.update_callback()

def setup_db_observer(update_callback):
    """Configura l'observer per la cartella db."""
    event_handler = DatabaseChangeHandler(update_callback)
    observer = Observer()
    observer.schedule(event_handler, BASE_DB_PATH, recursive=False)
    observer.start()
    return observer
