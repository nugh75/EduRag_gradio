import gradio as gr
import logging
from app.logging_config import configure_logging
from app.utils.database_handling import list_databases
from ui.chatbot_tab import create_chatbot_tab
from ui.db_management_tab import create_db_management_tab
from ui.document_management_tab import create_document_management_tab
from ui.info_tab import create_info_tab  # Importa la nuova tab
from ui.chunks_viewer_tab import create_chunks_viewer_tab  # Aggiungi l'import in cima al file

# Configura il logging
configure_logging()

def main():
    """Funzione principale che crea e lancia l'app Gradio."""
    logging.info("Avvio applicazione")
    try:
        with gr.Blocks() as rag_chatbot:
            gr.Markdown("# Chatbot basato su RAG")
            logging.info("Interfaccia Gradio inizializzata")
            
            # Prima ottiene tutti i riferimenti
            info_refs = create_info_tab()
            chat_refs = create_chatbot_tab()
            doc_refs = create_document_management_tab()
            chunks_refs = create_chunks_viewer_tab()  # Aggiungi il nuovo tab
            db_refs = create_db_management_tab # Crea la nuova tab delle informazioni
            
            # Crea dizionario completo dei riferimenti
            dropdowns = {
                "document": doc_refs,
                "chat": chat_refs,
                "info": info_refs,
                "chunks": chunks_refs  # Aggiungi il riferimento
            }
            
            # Crea i tab nell'ordine corretto
            chat_refs                                    # Tab 4: Chatbot (ultima tab)
            doc_refs  # Tab 2: Document Management
            db_refs(dropdowns) 
            chunks_refs  # Aggiungi il tab dei chunks
            info_refs                                    # Tab 5: Info (ultima tab)
            
            rag_chatbot.launch()
            
    except Exception as e:
        logging.error(f"Errore durante l'avvio: {str(e)}")

if __name__ == "__main__":
    main()