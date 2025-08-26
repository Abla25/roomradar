# 🏠 RoomRadar - Sistema Multi-Città

**RoomRadar** è un sistema intelligente per la gestione di annunci immobiliari multi-città, che combina feed RSS, AI per l'analisi del contenuto, e database Notion per una gestione centralizzata.

## 🌟 Caratteristiche Principali

### 🏙️ **Sistema Multi-Città**
- **Barcelona** 🇪🇸 (Catalonia, Spagna)
- **Roma** 🇮🇹 (Lazio, Italia)
- **Facilmente estendibile** per nuove città

### 🤖 **Intelligenza Artificiale**
- **Analisi automatica** del contenuto degli annunci
- **Scoring di affidabilità** basato su AI
- **Filtraggio intelligente** di contenuti non rilevanti
- **Integrazione OpenRouter API** per analisi avanzate

### 📊 **Gestione Dati**
- **Database Notion separati** per ogni città
- **Cache intelligente** per URL già processati
- **Feed RSS specifici** per ogni città
- **Zone mapping personalizzate** per ogni location

### 🎨 **Interfaccia Utente**
- **Design moderno** in stile Notion/Apple
- **Selezione città** con dropdown elegante
- **Filtri avanzati** (zona, prezzo, affidabilità, data)
- **Statistiche in tempo reale**
- **Responsive design** per tutti i dispositivi

## 🚀 Come Funziona

### 1. **Flusso Utente**

#### **Nuovi Utenti:**
1. **Apertura**: `index.html` → reindirizza automaticamente a `welcome.html`
2. **Selezione**: Sceglie città nella welcome page
3. **Salvataggio**: Preferenza salvata in localStorage
4. **Accesso**: Reindirizza a `index.html?city=selected`

#### **Utenti Esistenti:**
1. **Apertura**: `index.html` → carica direttamente città preferita
2. **Cambio**: Dropdown per cambiare città senza ricaricare pagina
3. **Persistenza**: localStorage mantiene la preferenza

#### **Modalità Incognito:**
1. **Apertura**: `index.html` → reindirizza a `welcome.html`
2. **Comportamento**: Come nuovo utente (localStorage vuoto)

### 2. **Processo di Elaborazione Dati**

#### **Raccolta Feed RSS:**
```bash
# Feed specifici per città - numero variabile
RSS_URL_BARCELONA_1=https://barcelona-feed1.com/feed
RSS_URL_BARCELONA_2=https://barcelona-feed2.com/feed
RSS_URL_BARCELONA_3=https://barcelona-feed3.com/feed
# ... aggiungi quanti ne servono

RSS_URL_ROMA_1=https://roma-feed1.com/feed
RSS_URL_ROMA_2=https://roma-feed2.com/feed
RSS_URL_ROMA_3=https://roma-feed3.com/feed
# ... aggiungi quanti ne servono
```

#### **Analisi AI:**
1. **Parsing RSS**: Estrazione dati dagli annunci
2. **Analisi OpenRouter**: Scoring affidabilità e analisi contenuto
3. **Filtraggio**: Rimozione annunci non rilevanti
4. **Mappatura Zone**: Conversione zone specifiche in macro-zone
5. **Salvataggio Notion**: Inserimento nel database appropriato

#### **Generazione Frontend:**
1. **Fetch Notion**: Recupero dati dal database
2. **Generazione JSON**: Creazione file `data_<città>.json`
3. **Aggiornamento Cache**: Salvataggio URL processati

## 📁 Struttura del Progetto

```
notion-rss-bot/
├── 🎨 Frontend
│   ├── index.html              # Portale principale con dropdown città
│   ├── welcome.html            # Pagina di benvenuto per selezione città
│   └── vector-cropped-cropped (1).svg  # Logo RoomRadar
│
├── 🐍 Backend Python
│   ├── main.py                 # Script principale per elaborazione RSS
│   ├── cities_config.py        # Configurazione centralizzata città
│   ├── process_cities.py       # Automazione per tutte le città
│   ├── censorship.py           # Filtri di contenuto
│   └── requirements.txt        # Dipendenze Python
│
├── 📊 Dati
│   ├── public/
│   │   └── data_barcelona.json # Dati frontend per Barcelona
│   ├── rejected_urls_cache_barcelona.json  # Cache URL scartati Barcelona
│   └── rejected_urls_cache_roma.json       # Cache URL scartati Roma
│
├── 🔧 Scripts
│   └── scripts/fetch_notion.js # Script Node.js per fetch Notion
│
├── ⚙️ Configurazione
│   ├── env.example             # Template variabili ambiente
│   ├── package.json            # Configurazione Node.js
│   └── .gitignore              # File da ignorare
│
├── 🚀 Deploy
│   ├── .github/workflows/      # GitHub Actions per automazione
│   └── CNAME                   # Configurazione dominio
│
└── 📚 Documentazione
    ├── README_MULTI_CITY.md    # Questo file
    └── MANUAL_SETUP_INSTRUCTIONS.md  # Istruzioni setup manuale
```

## ⚙️ Configurazione

### **GitHub Secrets Richiesti**

Configura i seguenti secrets nel tuo repository GitHub:

**Vai su GitHub → Settings → Secrets and variables → Actions**

```bash
# 🔑 API Keys
NOTION_API_KEY=your_notion_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# 🏢 Database Notion per ogni città
NOTION_DATABASE_ID_BARCELONA=your_barcelona_database_id
NOTION_DATABASE_ID_ROMA=your_roma_database_id

# 📡 Feed RSS specifici per città - numero variabile
# Aggiungi quanti feed RSS servono per ogni città (RSS_URL_CITY_1, RSS_URL_CITY_2, etc.)
RSS_URL_BARCELONA_1=https://barcelona-feed1.com/feed
RSS_URL_BARCELONA_2=https://barcelona-feed2.com/feed
RSS_URL_BARCELONA_3=https://barcelona-feed3.com/feed
RSS_URL_BARCELONA_4=https://barcelona-feed4.com/feed
RSS_URL_BARCELONA_5=https://barcelona-feed5.com/feed

RSS_URL_ROMA_1=https://roma-feed1.com/feed
RSS_URL_ROMA_2=https://roma-feed2.com/feed
RSS_URL_ROMA_3=https://roma-feed3.com/feed
RSS_URL_ROMA_4=https://roma-feed4.com/feed
RSS_URL_ROMA_5=https://roma-feed5.com/feed

# 🏙️ Città di default
DEFAULT_CITY=barcelona
```

### **Struttura Database Notion**

Ogni database Notion deve avere le seguenti proprietà:

| Proprietà | Tipo | Descrizione |
|-----------|------|-------------|
| `paraphrased_title` | title | Titolo riscritto dall'AI |
| `overview` | rich_text | Panoramica generata dall'AI |
| `original_description` | rich_text | Descrizione originale |
| `price` | rich_text | Prezzo dell'annuncio |
| `zone` | rich_text | Zona specifica |
| `zone_macro` | rich_text | Macro-zona mappata |
| `rooms` | rich_text | Numero di stanze |
| `reliability` | number | Punteggio affidabilità (1-5) |
| `rating_reason` | rich_text | Motivo del punteggio |
| `date_added` | date | Data di aggiunta |
| `link` | url | Link originale |
| `status` | select | Stato (active/expired/verification_needed) |
| `images` | url | Immagini dell'annuncio |

## 🚀 Installazione e Setup

### **1. Setup Iniziale**

```bash
# Clona il repository
git clone https://github.com/your-username/notion-rss-bot.git
cd notion-rss-bot

# Installa dipendenze Python
pip install -r requirements.txt

# Installa dipendenze Node.js
npm install

# Copia template ambiente
cp env.example .env
```

### **2. Configurazione**

1. **Configura GitHub Secrets** con le tue API keys e configurazioni
2. **Crea database Notion** per ogni città con la struttura corretta
3. **Configura feed RSS** specifici per ogni città nei secrets

### **3. Creazione File Data per Roma**

```bash
# Opzione A - Generazione automatica
CITY=roma python3 main.py
CITY=roma node scripts/fetch_notion.js

# Opzione B - File vuoto
echo '{"results": [], "totalRejectedCount": 0}' > public/data_roma.json
```

### **4. Test Locale (Opzionale)**

```bash
# Per test locale, crea un file .env temporaneo
cp env.example .env
# Modifica .env con i tuoi valori reali

# Avvia server locale
python3 -m http.server 8000

# Apri browser
open http://localhost:8000
```

## 🔄 Automazione

### **Processamento Automatico**

I dati vengono aggiornati automaticamente ogni ora tramite GitHub Actions.

### **Processamento Manuale (per test)**

```bash
# Per test locale, crea un file .env temporaneo
cp env.example .env
# Modifica .env con i tuoi valori reali

# Processa tutte le città
python3 process_cities.py

# Processa città specifica
CITY=barcelona python3 main.py
CITY=barcelona node scripts/fetch_notion.js
```

### **GitHub Actions**

Il sistema include workflow automatici:

- **Aggiornamento orario**: Processa feed RSS ogni ora
- **Fetch Notion**: Aggiorna dati frontend automaticamente
- **Commit automatici**: Salva modifiche su GitHub

## 🎯 Funzionalità Frontend

### **Dropdown Città**
- **Posizione**: Accanto al subtitle "Find your perfect room in"
- **Stile**: Coerente con design generale
- **Icona**: Pin rosso con contorno
- **Funzionalità**: Menu a tendina con solo altre città disponibili

### **Filtri Avanzati**
- **Zona**: Dropdown con macro-zone disponibili
- **Affidabilità**: Filtro per punteggio AI (1-5)
- **Prezzo**: Input numerico per prezzo massimo
- **Data**: Filtro per data pubblicazione
- **Ordinamento**: Per data, prezzo, affidabilità

### **Statistiche in Tempo Reale**
- **Active listings**: Numero annunci attivi
- **Posts rejected by AI**: Contatore contenuti scartati
- **Aggiornamento automatico**: Quando si cambia città

## 🔧 Manutenzione

### **Controlli Settimanali**
- Verifica feed RSS funzionanti
- Controllo log GitHub Actions
- Verifica aggiornamento dati

### **Controlli Mensili**
- Performance sistema
- Validità API keys
- Aggiornamento dipendenze

## 🐛 Risoluzione Problemi

### **Problemi Comuni**

1. **Feed RSS non funzionanti**
   - Verifica URL feed
   - Controlla formato RSS
   - Verifica accessibilità

2. **Database Notion non accessibile**
   - Verifica GitHub Secrets
   - Controlla permessi database
   - Verifica struttura proprietà

3. **Dati non aggiornati**
   - Controlla log GitHub Actions
   - Verifica GitHub Secrets
   - Controlla cache files

### **Log e Debug**

```bash
# Controlla log Python
python3 main.py

# Controlla log Node.js
node scripts/fetch_notion.js

# Verifica configurazione
python3 -c "import cities_config; print(cities_config.get_all_cities())"
```

## 📈 Estensione a Nuove Città

### **1. Aggiunta Configurazione**

Modifica `cities_config.py`:

```python
"nuova_citta": CityConfig(
    name="nuova_citta",
    display_name="Nuova Città",
    notion_database_id=os.environ.get("NOTION_DATABASE_ID_NUOVA_CITTA"),
    macro_zones=["Zona 1", "Zona 2", "Zona 3"],
    rss_urls=[
        os.environ.get("RSS_URL_NUOVA_CITTA_1", ""),
        os.environ.get("RSS_URL_NUOVA_CITTA_2", ""),
    ],
    zone_mapping={
        "Zona 1": ["quartiere1", "quartiere2"],
        "Zona 2": ["quartiere3", "quartiere4"],
    }
)
```

### **2. Aggiunta GitHub Secrets**

Aggiungi i seguenti secrets su GitHub:

- `NOTION_DATABASE_ID_NUOVA_CITTA` = your_database_id
- `RSS_URL_NUOVA_CITTA_1` = https://feed1.com/feed
- `RSS_URL_NUOVA_CITTA_2` = https://feed2.com/feed
- `RSS_URL_NUOVA_CITTA_3` = https://feed3.com/feed
- `...` = aggiungi quanti feed RSS servono

### **3. Creazione File Dati**

```bash
# Per test locale
CITY=nuova_citta python3 main.py
CITY=nuova_citta node scripts/fetch_notion.js

# Oppure esegui manualmente il GitHub Action
# Vai su GitHub → Actions → update-data.yml → Run workflow
```

## 🤝 Contributi

1. Fork il repository
2. Crea branch per feature (`git checkout -b feature/nuova-funzionalita`)
3. Commit modifiche (`git commit -am 'Aggiunge nuova funzionalità'`)
4. Push branch (`git push origin feature/nuova-funzionalita`)
5. Crea Pull Request

## 📄 Licenza

Questo progetto è sotto licenza MIT. Vedi il file `LICENSE` per dettagli.

## 📞 Supporto

Per supporto o domande:
- Apri un issue su GitHub
- Controlla la documentazione
- Verifica le istruzioni di setup

---

**RoomRadar** - Trova la tua stanza perfetta in qualsiasi città! 🏠✨
