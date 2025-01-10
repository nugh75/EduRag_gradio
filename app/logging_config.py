import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def configure_logging():
    """Configura le impostazioni di logging dell'applicazione."""
    # Percorso assoluto per la directory logs
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_directory = os.path.join(base_dir, "logs")
    
    # Crea la directory dei log se non esiste
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    # Nome file log con timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_directory, f"app_{timestamp}.log")
    
    # Configura il logger root
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Formattazione del log dettagliata
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s - (%(filename)s:%(lineno)d)'
    )
    
    # Handler per il file con rotazione (10MB per file)
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Handler per la console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Rimuovi handler esistenti e aggiungi i nuovi
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Test di scrittura
    logging.info(f"Logging inizializzato - File: {log_file}")
    logging.info("Test scrittura log")