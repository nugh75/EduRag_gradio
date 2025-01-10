import logging
import asyncio
import edge_tts
from app.config import VOICE_USER, VOICE_ASSISTANT
from pathlib import Path
from app.utils.markdowns_utils import clean_markdown


async def text_to_speech(text, voice_name, output_file):
    """Genera audio usando edge-tts"""
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_file)

def generate_speech(text, is_user=True):
    try:
        # Crea directory per audio temporanei
        audio_dir = Path("temp_audio")
        audio_dir.mkdir(exist_ok=True)
        
        # Seleziona voce e genera nome file
        voice = VOICE_USER if is_user else VOICE_ASSISTANT
        file_name = f"speech_{hash(text)}.mp3"
        output_path = audio_dir / file_name
        
        # Genera audio
        asyncio.run(text_to_speech(text, voice, str(output_path)))
        return str(output_path)
        
    except Exception as e:
        logging.error(f"Errore TTS: {e}")
        return None

def generate_chat_audio(chat_history):
    """Genera audio della conversazione con voci alternate"""
    try:
        audio_files = []
        audio_dir = Path("temp_audio")
        audio_dir.mkdir(exist_ok=True)
        
        # Genera audio per ogni messaggio
        for msg in chat_history:
            content = clean_markdown(msg["content"])
            if not content.strip():
                continue
                
            voice = VOICE_USER if msg["role"] == "user" else VOICE_ASSISTANT
            file_name = f"chat_{msg['role']}_{hash(content)}.mp3"
            output_path = audio_dir / file_name
            
            # Genera audio senza prefissi
            asyncio.run(text_to_speech(content, voice, str(output_path)))
            audio_files.append(str(output_path))
        
        # Combina tutti gli audio
        if audio_files:
            from pydub import AudioSegment

            combined = AudioSegment.empty()
            for audio_file in audio_files:
                segment = AudioSegment.from_mp3(audio_file)
                combined += segment
                
            final_path = audio_dir / f"chat_complete_{hash(str(chat_history))}.mp3"
            combined.export(str(final_path), format="mp3")
            return str(final_path)
            
        return None
        
    except Exception as e:
        logging.error(f"Errore generazione audio: {e}")
        return None