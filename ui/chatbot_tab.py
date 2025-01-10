# ui/chatbot_tab.py

import logging
import gradio as gr
from app.utils.database_handling import list_databases
from app.configs.prompts import SYSTEM_PROMPTS
from app.llm_handling import answer_question, LLMType
from app.utils.helpers import extract_text_from_files
from app.utils.voice_utils import *
from app.utils.markdowns_utils import clean_markdown


logging.basicConfig(level=logging.INFO)


def create_chatbot_tab():
    """Crea il tab 'Chatbot' dell'interfaccia Gradio."""
    
    def chat_upload_and_respond(files, chat_history, db_name):
        """Gestisce il caricamento dei file e aggiorna la chat con il contenuto."""
        if chat_history is None:
            chat_history = []
        
        if files is None:
            files = []
        
        file_names = "\n".join(file.name.split('/')[-1] for file in files if hasattr(file, 'name'))
        text = extract_text_from_files(files)
        
        chat_history.append({
            "role": "assistant",
            "content": f"📄 File caricati:\n{file_names}\n\nContenuto dei documenti caricati.\n{text}"
        })
        
        return chat_history

    def respond(message, chat_history, db_name, prompt_type, llm_type):
        if chat_history is None:
            chat_history = []

        # Mappatura dei modelli
        llm_mapping = {
        "openai - GPT-4o-Mini": LLMType.OPENAI_GPT_4O_MINI,
        "local - Qwen 7B": LLMType.LOCAL_QWEN,
        "local - Phi-3 Mini": LLMType.LOCAL_PHI,
        "deepseek - DeepSeek Chat": LLMType.DEEPSEEK,
        "anthropic - Cloud": LLMType.ANTHROPIC  # Aggiunto il nuovo modello Cloud
        }
        
        selected_llm = llm_mapping.get(llm_type, LLMType.OPENAI_GPT_4O_MINI)
        
        messages = answer_question(
            message, 
            db_name, 
            prompt_type=prompt_type.split(" - ")[0],
            llm_type=selected_llm
        )
        
        chat_history.extend(messages)
        return "", chat_history

    def clear_chat():
        """Pulisce la cronologia della chat."""
        return [], []

    def format_conversation_for_download(chat_history):
        """Formatta la cronologia della chat per il download."""
        if not chat_history:
            return "Nessuna conversazione da scaricare"
        
        formatted_text = []
        for msg in chat_history:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"]
            formatted_text.append(f"{role}: {content}\n")
        
        return "\n".join(formatted_text)

    def download_conversation(chat_history):
        """Prepara il file di testo per il download."""
        conversation_text = format_conversation_for_download(chat_history)
        
        # Crea un file temporaneo con la conversazione
        import tempfile
        import os
        from pathlib import Path
        
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "conversazione.txt")
        
        # Assicurati che il contenuto sia in UTF-8
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(conversation_text)
        
        return str(Path(temp_path).absolute())

    # def download_audio(chat_history):
    #     """Scarica l'ultimo messaggio audio dalla chat"""
    #     try:
    #         if not chat_history:
    #             gr.Warning("Nessun messaggio nella chat")
    #             return None
                
    #         # Prendi l'ultimo messaggio assistant
    #         for msg in reversed(chat_history):
    #             if msg["role"] == "assistant" and "audio" in msg:
    #                 audio_path = msg["audio"]
    #                 if audio_path and os.path.exists(audio_path):
    #                     return audio_path
                    
    #         gr.Warning("Nessun audio disponibile per l'ultima risposta")
    #         return None
                
    #     except Exception as e:
    #         gr.Error(f"Errore durante il download dell'audio: {str(e)}")
            # return None

    def format_conversation_for_audio(chat_history):
        """Formatta la conversazione per la sintesi vocale"""
        audio_text = []
        for msg in chat_history:
            role = "Utente" if msg["role"] == "user" else "Assistente"
            audio_text.append(f"{role} dice: {msg['content']}")
        return "\n".join(audio_text)

    # def generate_conversation_audio(chat_history):
    #     """Genera audio della conversazione completa"""
    #     try:
    #         if not chat_history:
    #             gr.Warning("Nessun messaggio nella chat")
    #             return None
                
    #         conversation_text = format_conversation_for_audio(chat_history)
    #         audio_path = generate_speech(conversation_text, is_user=False)
            
    #         if audio_path and os.path.exists(audio_path):
    #             return audio_path
    #         else:
    #             gr.Warning("Errore nella generazione dell'audio")
    #             return None
                
    #     except Exception as e:
    #         gr.Error(f"Errore: {str(e)}")
    #         return None

    def convert_chat_to_audio(chat_history):
        if not chat_history:
            gr.Warning("Nessun messaggio da convertire")
            return None
            
        audio_path = generate_chat_audio(chat_history)
        if audio_path:
            return audio_path
        else:
            gr.Warning("Errore nella generazione dell'audio")
            return None

    # Ottieni la lista aggiornata dei database
    databases = list_databases()

    with gr.Tab("Chatbot"):
        # Prima riga: Dropdown selettori
        with gr.Row():
            with gr.Column(scale=1):
                db_name_chat = gr.Dropdown(
                    choices=list_databases(),  # Lista dinamica dei database
                    label="Seleziona Database",
                    value=list_databases()[0] if list_databases() else None
                )
            
            with gr.Column(scale=1):
                prompt_selector = gr.Dropdown(
                    choices=list(SYSTEM_PROMPTS.keys()),  # Usa le chiavi da SYSTEM_PROMPTS
                    label="Seleziona Stile Risposta",
                    value="tutor"
                )
            
            with gr.Column(scale=1):
                llm_selector = gr.Dropdown(
                    choices=[
                        "openai - GPT-4o-Mini",
                        "local - Qwen 7B", 
                        "local - Phi-3 Mini",
                        "deepseek - DeepSeek Chat",
                        "anthropic - Cloud"  # Aggiungi il nuovo modello Cloud
                    ],
                    label="Seleziona Modello",
                    value="openai - GPT-4o-Mini"
                )
        
        # Chatbot e input
        chatbot = gr.Chatbot(label="Conversazione", type="messages")
        question_input = gr.Textbox(
            label="Fai una domanda",
            placeholder="Scrivi qui la tua domanda...",
            lines=2
        )
        
        # Bottoni per azioni
        with gr.Row():
            ask_button = gr.Button("Invia")
            upload_button = gr.Button("Carica Documenti")
            download_button = gr.Button("💾 Scarica Conversazione")
            clear_button = gr.Button("Pulisci Chat")       
            
        # box
        with gr.Row():
            file_input = gr.File(
                label="Carica PDF/Docx/TXT per la conversazione", 
                file_types=[".pdf", ".docx", ".txt"], 
                file_count="multiple",
                height="10px"
                          )
            download_file = gr.File(
                label="Download Conversazione",
                visible=True,
                interactive=False
                )
        
        # Stato della chat
        chat_state = gr.State([])

             
        with gr.Row():
            with gr.Column(scale=1):
                audio_button = gr.Button("🎤 Genera Audio Chat")
                audio_output = gr.Audio(label="Audio", visible=True)
            
        audio_button.click(
            fn=convert_chat_to_audio,
            inputs=[chatbot],
            outputs=[audio_output]
        )

        # Eventi per i bottoni
        upload_button.click(
            fn=chat_upload_and_respond,
            inputs=[file_input, chat_state, db_name_chat],
            outputs=chatbot
        )

        ask_button.click(
            fn=respond,
            inputs=[question_input, chat_state, db_name_chat, prompt_selector, llm_selector],  # Aggiungi il selettore del modello
            outputs=[question_input, chatbot]
        )

        clear_button.click(
            fn=clear_chat,
            outputs=[chatbot, chat_state]
        )

        # Aggiungi evento per il download
        download_button.click(
            fn=download_conversation,
            inputs=[chatbot],
            outputs=[download_file]
        )
 

    # Ritorna il riferimento al dropdown corretto
    return {"db_selector": db_name_chat}
