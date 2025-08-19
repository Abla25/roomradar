# 🔒 Workflow di Censura Database Notion

Questo documento spiega come utilizzare il workflow GitHub Actions per censurare tutti i dati esistenti nel database Notion.

## 📋 Prerequisiti

Prima di eseguire il workflow, assicurati che i seguenti secrets siano configurati su GitHub:

1. **NOTION_API_KEY**: La tua API key di Notion
2. **NOTION_DATABASE_ID**: L'ID del database Notion

### Come configurare i secrets:

1. Vai su GitHub → Repository → Settings → Secrets and variables → Actions
2. Clicca "New repository secret"
3. Aggiungi:
   - `NOTION_API_KEY` = `secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - `NOTION_DATABASE_ID` = `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## 🚀 Come Eseguire il Workflow

### Passo 1: Attiva il Workflow

1. Vai su GitHub → Repository → Actions
2. Clicca su "Censor Notion Database" nella lista dei workflow
3. Clicca "Run workflow" (pulsante blu)
4. Seleziona il branch (solitamente `main`)
5. Clicca "Run workflow"

### Passo 2: Monitora l'Esecuzione

Il workflow eseguirà i seguenti step:

1. **Checkout repository**: Scarica il codice
2. **Setup Python**: Configura l'ambiente Python 3.11
3. **Install dependencies**: Installa le dipendenze da `requirements.txt`
4. **Create censorship script**: Crea lo script di censura temporaneo
5. **Run database censorship**: Esegue la censura del database Notion
6. **Commit and push changes**: Committa e pusha le modifiche a `data.json`
7. **Cleanup**: Rimuove i file temporanei

### Passo 3: Verifica i Risultati

Dopo l'esecuzione, verifica che:

1. **Database Notion**: I record hanno le descrizioni censurate
2. **File data.json**: Aggiornato con i dati censurati
3. **Frontend**: Mostra i dati censurati correttamente

## 📊 Cosa Fa il Workflow

### 🔍 Recupero Dati
- Legge tutti i record dal database Notion con status "Attivo"
- Gestisce la paginazione automaticamente (100 record per volta)

### 🔒 Censura Dati
- **Numeri di telefono**: Sostituiti con `[PHONE NUMBER CENSORED]`
- **WhatsApp/Telegram**: Sostituiti con `[MESSAGING CONTACT CENSORED]`
- **Email**: Sostituite con `[EMAIL CENSORED]`
- **Codici fiscali**: Sostituiti con `[FISCAL CODE CENSORED]`
- **Partite IVA**: Sostituite con `[VAT NUMBER CENSORED]`

### 📝 Aggiornamento
- Aggiorna i record nel database Notion
- Aggiorna il file `public/data.json`
- Committa e pusha le modifiche automaticamente

## ⚠️ Attenzioni Importanti

### 🔐 Sicurezza
- **ATTENZIONE**: Questo workflow modifica permanentemente i dati nel database
- I dati sensibili vengono sostituiti e non possono essere recuperati
- Assicurati di avere un backup se necessario

### 🕐 Tempo di Esecuzione
- Il workflow può richiedere diversi minuti per completarsi
- Dipende dal numero di record nel database
- Monitora i log per vedere il progresso

### 🔄 Una Tantum
- Questo workflow è progettato per essere eseguito una sola volta
- Dopo l'esecuzione, tutti i nuovi dati verranno censurati automaticamente dal sistema principale

## 🐛 Troubleshooting

### Errore: "Variabili d'ambiente non disponibili"
- Verifica che i secrets siano configurati correttamente
- Controlla i nomi dei secrets (maiuscole/minuscole)

### Errore: "Errore nel recupero record"
- Verifica che l'API key di Notion sia valida
- Controlla che il database ID sia corretto
- Verifica i permessi del database

### Errore: "Errore aggiornamento record"
- Controlla i permessi di scrittura sul database
- Verifica che la struttura del database sia corretta

## 📈 Statistiche

Il workflow fornisce statistiche dettagliate:

- **Record processati**: Numero totale di record nel database
- **Record aggiornati**: Record che contenevano dati sensibili
- **Elementi censurati**: Numero totale di elementi sensibili trovati

## 🧹 Pulizia

Dopo l'esecuzione:

1. Il workflow rimuove automaticamente i file temporanei
2. Il file `data.json` viene aggiornato e committato
3. I log dell'esecuzione sono disponibili nella sezione Actions

## 📞 Supporto

Se incontri problemi:

1. Controlla i log del workflow in GitHub Actions
2. Verifica la configurazione dei secrets
3. Controlla i permessi del database Notion
4. Crea un issue su GitHub se necessario

---

**Nota**: Questo workflow è progettato per essere eseguito una sola volta per censurare i dati esistenti. Dopo l'esecuzione, il sistema principale (`main.py`) si occuperà di censurare automaticamente tutti i nuovi dati in ingresso.
