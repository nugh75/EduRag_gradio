import logging
import os
import shutil
from app.utils.extract_utils import extract_text_from_pdf, extract_text_from_docx
from datetime import datetime

def extract_text_from_files(files):
    """Estrae il testo dai file caricati."""
    if not files:
        return ""
    
    extracted_text = []
    
    # Usa il percorso assoluto della cartella Temp_file
    temp_dir = "/Users/danieledragoni/hugginface/Edurag_beta/app/Temp_file"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    for file in files:
        temp_path = None
        try:
            file_extension = os.path.splitext(file.name)[1].lower()
            
            # Crea un nome file univoco nella cartella Temp_file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_filename = f"temp_{timestamp}{file_extension}"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            # Copia il file da Gradio alla nostra cartella Temp_file
            shutil.copy2(file.name, temp_path)
            
            logging.info(f"File temporaneo creato in: {temp_path}")
            
            # Estrai il testo in base al tipo di file
            if file_extension == '.pdf':
                try:
                    text = extract_text_from_pdf(temp_path)
                    extracted_text.append(text)
                except Exception as e:
                    logging.error(f"Errore nell'elaborazione del PDF {file.name}: {str(e)}")
                    extracted_text.append(f"[Errore nell'elaborazione del PDF {file.name}. Dettaglio: {str(e)}]")
            
            elif file_extension == '.docx':
                text = extract_text_from_docx(temp_path)
                extracted_text.append(text)
            
            elif file_extension == '.txt':
                with open(temp_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    extracted_text.append(text)
                    
        except Exception as e:
            logging.error(f"Errore durante l'elaborazione del file {file.name}: {str(e)}")
            extracted_text.append(f"[Errore nell'elaborazione del file {file.name}]")
            
        finally:
            # Pulisci il file temporaneo
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    logging.error(f"Errore nella pulizia del file temporaneo: {str(e)}")

    return "\n\n".join(extracted_text)
