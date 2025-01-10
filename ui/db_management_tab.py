import gradio as gr
from app.utils.database_handling import create_database, modify_database, delete_database, list_databases

def create_db_management_tab(dropdowns):
    databases = list_databases()
    
    def update_dropdowns():
        updated_dbs = list_databases()
        # Aggiorna tutti i dropdown dell'applicazione (5 invece di 4)
        return [gr.update(choices=updated_dbs) for _ in range(5)]
    
    
        
    with gr.Tab("Gestione Database"):
        gr.Markdown("## Operazioni sui Database")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Crea Database")
                db_name_input = gr.Textbox(label="Nome Nuovo Database")
                create_db_button = gr.Button("Crea Database")
                create_output = gr.Textbox(label="Stato Creazione")
            
            with gr.Column():
                gr.Markdown("### Rinomina Database")
                modify_db_old_name = gr.Dropdown(
                    choices=databases, 
                    label="Database da Rinominare"
                )
                modify_db_new_name = gr.Textbox(label="Nuovo Nome")
                modify_db_button = gr.Button("Rinomina Database")
                modify_output = gr.Textbox(label="Stato Modifica")
            
            with gr.Column():
                gr.Markdown("### Elimina Database") 
                delete_db_dropdown = gr.Dropdown(
                    choices=databases, 
                    label="Database da Eliminare"
                )
                delete_db_button = gr.Button("Elimina Database")
                delete_output = gr.Textbox(label="Stato Eliminazione")
        
        # Eventi per i bottoni di gestione DB
        create_db_button.click(
            fn=create_database,
            inputs=db_name_input,
            outputs=create_output
        ).then(
            fn=update_dropdowns,
            outputs=[
                modify_db_old_name,                  # db_management_tab
                delete_db_dropdown,                  # db_management_tab  
                dropdowns["document"]["upload"],     # document_management_tab
                dropdowns["document"]["list"],       # document_management_tab
                dropdowns["chat"]["db_selector"]     # chatbot_tab
            ]
        )

        modify_db_button.click(
            fn=modify_database,
            inputs=[modify_db_old_name, modify_db_new_name],
            outputs=modify_output
        ).then(
            fn=update_dropdowns,
            outputs=[
                modify_db_old_name,                  # db_management_tab
                delete_db_dropdown,                  # db_management_tab
                dropdowns["document"]["upload"],     # document_management_tab
                dropdowns["document"]["list"],       # document_management_tab
                dropdowns["chat"]["db_selector"]     # chatbot_tab
            ]
        )

        delete_db_button.click(
            fn=delete_database,
            inputs=delete_db_dropdown,
            outputs=delete_output
        ).then(
            fn=update_dropdowns,
            outputs=[
                modify_db_old_name,                  # db_management_tab
                delete_db_dropdown,                  # db_management_tab
                dropdowns["document"]["upload"],     # document_management_tab
                dropdowns["document"]["list"],       # document_management_tab
                dropdowns["chat"]["db_selector"]     # chatbot_tab
            ]
        )
    
    # Ritorna i componenti che vogliamo poter aggiornare/agganciare
    return [modify_db_old_name, delete_db_dropdown, create_db_button, modify_db_button, delete_db_button]
