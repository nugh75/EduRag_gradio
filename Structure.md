
# Struttura dell'Applicazione EduRag Beta

## Diagramma dell'Architettura
```mermaid
graph TD
    A[app.py - Main Application] --> B[UI Layer]
    A --> C[App Layer]
    A --> D[Config Layer]

    B --> B1[chatbot_tab.py]
    B --> B2[db_management_tab.py]
    B --> B3[document_management_tab.py]
    B --> B4[info_tab.py]

    C --> C1[llm_handling.py]
    C --> C2[document_handling.py]
    C --> C3[database_handling.py]
    C --> C4[logging_config.py]

    D --> D1[config.py]
    D --> D2[prompts.py]

    C1 --> E1[embedding_utils]
    C1 --> E2[voice_utils]
    
    C2 --> F1[FAISS Vectorstore]
    C2 --> F2[File Processing]

    D1 --> G1[LLM Configs]
    D1 --> G2[Embedding Configs]
    D1 --> G3[Voice Configs]
```

## Componenti Principali

### 1. UI Layer
- chatbot_tab.py: Interfaccia principale del chatbot
- db_management_tab.py: Gestione database
- document_management_tab.py: Gestione documenti
- info_tab.py: Informazioni sul sistema

### 2. App Layer
- llm_handling.py: Gestione LLM e embeddings
- document_handling.py: Processamento documenti
- database_handling.py: Gestione database FAISS
- logging_config.py: Configurazione logging

### 3. Config Layer
- config.py: Configurazioni generali
- prompts.py: Template dei prompt

### 4. Utilities
- embedding_utils: Gestione embeddings
- voice_utils: Generazione audio

### 5. Storage
- FAISS Vectorstore
- File system per documenti
- Metadata in JSON

## Caratteristiche Principali
- Struttura modulare
- Separazione delle responsabilità
- Facile manutenzione
- Scalabilità del sistema
- Gestione efficiente delle dipendenze
```