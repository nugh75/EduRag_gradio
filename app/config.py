import os
from dotenv import load_dotenv
from enum import Enum
from openai import OpenAI
from pathlib import Path
import anthropic
from langchain_community.chat_models import ChatAnthropic



# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Configurazione del modello
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY non trovata. Verifica il file .env")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY non trovata. Verifica il file .env")

class LLMType(Enum):
    OPENAI_GPT_4O_MINI = "openai - GPT-4o-mini"
    LOCAL_QWEN = "local - Qwen 7B"
    LOCAL_PHI = "local - Phi-3 Mini"
    DEEPSEEK = "deepseek - DeepSeek Chat"
    ANTHROPIC = "anthropic - Cloud"  # Aggiungi il tipo ANTHROPIC

# Configurazione modelli
LLM_CONFIGS = {
    LLMType.OPENAI_GPT_4O_MINI: {
        "client": lambda: OpenAI(api_key=OPENAI_API_KEY),
        "model": "gpt-4o-mini",
        "base_url": None
    },
    LLMType.LOCAL_QWEN: {
        "client": lambda: OpenAI(base_url="http://192.168.43.199:1234/v1", api_key="not-needed"),
        "model": "qwen2.5-coder-7b-instruct",
        "base_url": "http://192.168.43.199:1234/v1"
    },
    LLMType.LOCAL_PHI: {
        "client": lambda: OpenAI(base_url="http://192.168.43.199:1234/v1", api_key="not-needed"),
        "model": "phi-3.5-mini-ita",
        "base_url": "http://192.168.43.199:1234/v1"
    },
    LLMType.DEEPSEEK: {
        "client": lambda: OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1"),
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com/v1"
    }
}

EMBEDDING_CONFIG = {
    "model_name": "sentence-transformers/multi-qa-mpnet-base-dot-v1",
    "chunk_size": 2000,
    "chunk_overlap": 100,
    "min_similarity": 0.7
}

LLM_CONFIGS_EXTENDED = {
    "temperature": 0.7,
    "max_tokens": 2048
}

# Aggiungi questa costante
EMBEDDING_MODEL = "sentence-transformers/multi-qa-mpnet-base-dot-v1"

# Definisci il percorso base per i database
BASE_DB_PATH = "db"

# Configurazione modelli
# Aggiungi la configurazione per l'API di Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY non trovata. Verifica il file .env")

# Configurazione per l'API di Anthropic
LLM_CONFIGS[LLMType.ANTHROPIC] = {
    "client": lambda: anthropic(api_key=ANTHROPIC_API_KEY),
    "model": "claude-3-5-sonnet-20241022",  # Sostituisci con il nome del modello appropriato
    "base_url": "https://api.anthropic.com/v1"
}
VOICE_USER = "it-IT-DiegoNeural"      # Voce maschile utente
VOICE_ASSISTANT = "it-IT-ElsaNeural"   # Voce femminile assistente
