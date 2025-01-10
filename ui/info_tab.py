import gradio as gr

def create_info_tab():
    """Crea il tab con le informazioni sul chatbot"""
    with gr.Tab("Info"):
        gr.Markdown("""

### EduRag\_beta (Chatbot basato su RAG)

Questo chatbot utilizza la tecnologia RAG per migliorare le conversazioni tramite il recupero e la generazione di informazioni basate su documenti caricati e su database preconfigurati. È progettato per supportare diverse attività educative, formative o di consulenza attraverso l'interazione con un Large Language Model (LLM) personalizzabile.

#### Funzionalità principali:

1. **Selezione delle conoscenze e del modello LLM**

   - Gli utenti possono selezionare un database specifico di conoscenze da cui il chatbot recupera informazioni (ad esempio, "Orientamento") e scegliere un agente con istruzioni specifiche per personalizzare il tipo di conversazione (es. “tutor”).
   - I modelli disponibili sono due: **OpenAI gpt-4o-mini** e un modello locale gestito tramite LM Studio. Il modello locale può variare a seconda di quello che si ha disponibile nel sistema.

2. **Interfaccia di conversazione**

   - L'utente può interagire con il chatbot digitando domande o richieste nella finestra dedicata.
   - Il chatbot risponde utilizzando le informazioni disponibili nei documenti caricati o nel database selezionato.

3. **Caricamento documenti**

   - Gli utenti possono caricare documenti in formato PDF, DOCX o TXT per arricchire le conoscenze del chatbot. Il contenuto dei documenti caricati viene inserito direttamente nella storia della conversazione, permettendo al sistema di utilizzarlo per rispondere in modo contestualizzato.

4. **Gestione della conversazione**

   - È possibile scaricare una copia della conversazione avvenuta con il chatbot in formato testo per conservarne una traccia.
   - L'interfaccia permette di generare un file audio della chat, utile per chi preferisce ascoltare le conversazioni anziché leggerle.

5. **Gestione documenti e database**

   - La sezione "Gestione Documenti" consente di visualizzare, caricare, modificare ed eliminare i documenti che fanno parte dei diversi database di conoscenza a disposizione del chatbot.
   - La sezione "Gestione Database" permette di caricare, eliminare e modificare il nome dei database di conoscenza da cui il chatbot attinge le informazioni.

6. **Nuove funzionalità**

   - Il chatbot è predisposto per futuri aggiornamenti e nuove funzionalità, ampliando le sue capacità. Alcune di queste funzionalità, come la gestione avanzata dei database di conoscenza, sono attualmente in fase di sviluppo e non ancora operative.

#### Agenti disponibili nel sistema:

1. **Tutor**: Agisce come un tutor didattico di nome Valter, offrendo spiegazioni chiare e supporto personalizzato per facilitare l’apprendimento degli utenti.

2. **Scientist**: Si comporta come uno scienziato esperto, analizzando i contesti da una prospettiva scientifica e fornendo risposte dettagliate e basate su un approccio analitico.

3. **Expert**: Fornisce risposte tecniche e specifiche, concentrandosi sull'approfondimento di tematiche complesse in vari settori.

4. **Teacher**: Assume il ruolo di un insegnante paziente, spiegando concetti in modo semplice e comprensibile, adottando un tono pedagogico.

5. **Orientatore**: Si presenta come un tutor orientatore serio e professionale, specializzato nel guidare gli studenti delle scuole verso scelte consapevoli per il loro percorso formativo e professionale. Fornisce supporto empatico, dettagliato e stimola la riflessione autonoma dello studente.

6. **Coach didattico**: Assiste gli insegnanti nella pianificazione delle lezioni. Collabora attivamente con loro per creare piani didattici personalizzati che includano diverse tecniche di insegnamento, assicurando il raggiungimento degli obiettivi di apprendimento.

 """)
    
    return {}
