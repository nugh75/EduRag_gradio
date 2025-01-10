import pdfplumber
from docx import Document
import logging
import io

def extract_text_from_pdf(file_path):
    """
    Estrae il testo da un file PDF usando pdfplumber.
    
    Args:
        file_path: Percorso del file PDF
        
    Returns:
        str: Testo estratto dal PDF o messaggio di errore
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            text = []
            for page in pdf.pages:
                try:
                    page_text = page.extract_text() or ""
                    text.append(page_text)
                except Exception as e:
                    logging.warning(f"Errore nell'estrazione della pagina: {str(e)}")
                    continue
            
            extracted_text = "\n".join(text)
            if not extracted_text.strip():
                raise ValueError("Nessun testo estratto dal PDF")
                
            return extracted_text
            
    except Exception as e:
        logging.error(f"Errore nella lettura del PDF: {str(e)}")
        raise

def extract_text_from_docx(file_path):
    """
    Estrae il testo da un file DOCX.
    
    Args:
        file_path: Percorso del file DOCX
        
    Returns:
        str: Testo estratto dal documento Word
    """
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text