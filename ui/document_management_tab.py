import gradio as gr
import logging
from app.document_handling import upload_and_index, list_indexed_files, delete_file_from_database
from app.utils.database_handling import list_databases

def create_document_management_tab():
    """Crea il tab 'Gestione Documenti' dell'interfaccia Gradio."""
    
    def update_dropdowns():
        """Aggiorna localmente i dropdown con la lista aggiornata dei database."""
        updated_dbs = list_databases()
        logging.info(f"Aggiornamento dropdown con databases: {updated_dbs}")
        return [
            gr.update(choices=updated_dbs),
            gr.update(choices=updated_dbs)
        ]

    def upload_and_index_callback(files, title, author, db_name):
        try:
            success, message, details = upload_and_index(files, title, author, db_name)
            if success:
                return message, list_databases(), list_databases()
            else:
                return message, list_databases(), list_databases()
        except Exception as e:
            error_msg = f"Errore durante l'upload: {e}"
            logging.error(error_msg)
            return error_msg, list_databases(), list_databases()

    def list_files_callback(db_name):
        """Elenca i file indicizzati nel database conoscenze specificato."""
        files = list_indexed_files(db_name)
        return files

    def delete_file_callback(file_name, db_name):
        """Elimina un file dal database e aggiorna la lista."""
        status = delete_file_from_database(file_name, db_name)
        return status

    # Ottieni la lista dei database
    databases = list_databases()

    with gr.Tab("Gestione Documenti"):
        with gr.Column():
            gr.Markdown("### Carica Documenti")
            with gr.Row():
                file_input = gr.File(
                    label="Carica i tuoi documenti", 
                    file_types=[".txt", ".pdf", ".docx"], 
                    file_count="multiple"
                )
                db_name_upload = gr.Dropdown(
                    choices=databases, 
                    label="Seleziona database conoscenze"
                )
            
            with gr.Row():
                title_input = gr.Textbox(label="Titolo del documento")
                author_input = gr.Textbox(label="Autore")
            
            upload_button = gr.Button("Indicizza Documenti")
            upload_output = gr.Textbox(label="Stato Upload")

            gr.Markdown("### Gestione File")
            with gr.Row():
                db_name_list = gr.Dropdown(
                    choices=databases,
                    label="Database conoscenze"
                )
                list_button = gr.Button("Lista File")
            list_output = gr.Textbox(label="File nel Database conoscenze")

            with gr.Row():
                delete_file_input = gr.Textbox(label="Nome File da Eliminare")
                delete_file_button = gr.Button("Elimina File")
            delete_file_output = gr.Textbox(label="Stato Eliminazione")

        # Eventi modificati
        upload_button.click(
            fn=upload_and_index_callback,
            inputs=[file_input, title_input, author_input, db_name_upload],
            outputs=[upload_output, db_name_upload, db_name_list]
        )

        list_button.click(
            fn=list_files_callback,
            inputs=[db_name_list],
            outputs=list_output
        )

        delete_file_button.click(
            fn=delete_file_callback,
            inputs=[delete_file_input, db_name_list],
            outputs=delete_file_output
        ).then(
            fn=update_dropdowns,
            outputs=[db_name_upload, db_name_list]
        ).then(
            fn=list_files_callback,
            inputs=[db_name_list],
            outputs=list_output
        )

    return {"upload": db_name_upload, "list": db_name_list}
