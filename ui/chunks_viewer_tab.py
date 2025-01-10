import gradio as gr
import logging
import os
import json
from langchain.vectorstores import FAISS
from app.document_handling import get_embeddings
from app.config import BASE_DB_PATH
from app.utils.database_handling import list_databases


def create_chunks_viewer_tab():
    """Crea il tab per visualizzare i chunks dei database."""
    
    def load_chunks(db_name):
        """Carica la lista dei chunks dal database selezionato."""
        if not db_name:
            return gr.Dropdown(choices=[], interactive=False), "Seleziona un database"
            
        try:
            metadata_path = os.path.join(BASE_DB_PATH, f"faiss_index_{db_name}", "metadata.json")
            vectorstore_path = os.path.join(BASE_DB_PATH, f"faiss_index_{db_name}")
            
            # Carica metadati e vectorstore
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            embeddings = get_embeddings()
            vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
            
            # Crea lista di chunks con formato "Chunk X - Titolo (File)"
            chunk_list = []
            current_index = 0
            
            for doc in metadata:
                for i in range(doc['chunks']):
                    # Recupera il contenuto del chunk per verifica
                    doc_id = list(vectorstore.docstore._dict.keys())[current_index]
                    chunk_metadata = vectorstore.docstore._dict[doc_id].metadata
                    chunk_list.append(f"Chunk {current_index} - {doc['title']} ({doc['filename']})")
                    current_index += 1
            
            return gr.Dropdown(choices=chunk_list, interactive=True), ""
        except Exception as e:
            logging.error(f"Errore nel caricamento chunks: {e}")
            return gr.Dropdown(choices=[], interactive=False), f"Errore: {e}"

    def inspect_chunk(db_name, chunk_id):
        """Recupera il contenuto del chunk selezionato."""
        if not db_name or not chunk_id:
            return "Seleziona un database e un chunk"
            
        try:
            db_path = os.path.join(BASE_DB_PATH, f"faiss_index_{db_name}")
            embeddings = get_embeddings()
            vectorstore = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
            
            # Estrai il numero del chunk
            chunk_num = int(chunk_id.split(" - ")[0].replace("Chunk ", ""))
            
            # Recupera il chunk usando l'ID univoco
            doc_ids = list(vectorstore.docstore._dict.keys())
            chunk_content = vectorstore.docstore._dict[doc_ids[chunk_num]].page_content
            return chunk_content

        except Exception as e:
            logging.error(f"Errore nell'ispezione del chunk: {e}")
            return f"Errore nel recupero del contenuto: {e}"

    with gr.Tab("Visualizza Chunks"):
        gr.Markdown("## Ispeziona Chunks dei Database")
        
        with gr.Row():
            with gr.Column():
                # Selettori
                db_selector = gr.Dropdown(
                    choices=list_databases(),
                    label="Seleziona Database",
                    value=list_databases()[0] if list_databases() else None
                )
                chunk_selector = gr.Dropdown(
                    choices=[],
                    label="Seleziona Chunk",
                    interactive=False
                )
                inspect_button = gr.Button("Visualizza Contenuto")
            
            with gr.Column():
                # Area visualizzazione contenuto
                chunk_content = gr.TextArea(
                    label="Contenuto del Chunk",
                    interactive=False,
                    lines=20
                )
                error_box = gr.Textbox(
                    label="Status",
                    visible=True,
                    interactive=False
                )

        # Eventi
        db_selector.change(
            fn=load_chunks,
            inputs=[db_selector],
            outputs=[chunk_selector, error_box]
        )

        inspect_button.click(
            fn=inspect_chunk,
            inputs=[db_selector, chunk_selector],
            outputs=[chunk_content]
        )

    return {"db_selector": db_selector}