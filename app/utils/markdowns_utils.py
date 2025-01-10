import re

# =====================================
# Funzioni relative al Markdown
# =====================================

def clean_markdown(text):
    """Rimuove markdown dal testo"""
    text = re.sub(r'```[\s\S]*?```', '', text)  # blocchi codice
    text = re.sub(r'`.*?`', '', text)           # codice inline
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # link
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # italic
    return text.strip()