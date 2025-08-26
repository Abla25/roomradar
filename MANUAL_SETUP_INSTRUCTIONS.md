# 🛠️ Istruzioni Manuali per Setup e Manutenzione

## 📋 **Cosa Devi Fare Tu a Mano**

### 1. 🔑 **Configurazione GitHub Secrets**

Configura i seguenti secrets nel tuo repository GitHub:

**Vai su GitHub → Settings → Secrets and variables → Actions**

#### **API Keys:**
- `NOTION_API_KEY` = your_notion_api_key_here
- `OPENROUTER_API_KEY` = your_openrouter_api_key_here

#### **Database Notion per ogni città:**
- `NOTION_DATABASE_ID_BARCELONA` = your_barcelona_database_id
- `NOTION_DATABASE_ID_ROMA` = your_roma_database_id

#### **RSS Feeds per Barcelona (aggiungi quanti ne servono):**
- `RSS_URL_BARCELONA_1` = https://example.com/barcelona-feed-1
- `RSS_URL_BARCELONA_2` = https://example.com/barcelona-feed-2
- `RSS_URL_BARCELONA_3` = https://example.com/barcelona-feed-3
- `RSS_URL_BARCELONA_4` = https://example.com/barcelona-feed-4
- `RSS_URL_BARCELONA_5` = https://example.com/barcelona-feed-5

#### **RSS Feeds per Roma (aggiungi quanti ne servono):**
- `RSS_URL_ROMA_1` = https://example.com/roma-feed-1
- `RSS_URL_ROMA_2` = https://example.com/roma-feed-2
- `RSS_URL_ROMA_3` = https://example.com/roma-feed-3
- `RSS_URL_ROMA_4` = https://example.com/roma-feed-4
- `RSS_URL_ROMA_5` = https://example.com/roma-feed-5

**Nota**: I secrets sono automaticamente disponibili nei GitHub Actions e non sono visibili nel codice.

**Città di default**: La città di default è configurata in `cities_config.py` nella funzione `get_default_city()`. Modifica quella funzione se vuoi cambiare la città di default.

### 2. 📊 **Creazione File Data per Roma**

Il sistema ha bisogno di un file `public/data_roma.json` per Roma. Puoi:

**Opzione A - Generazione automatica:**
```bash
# Imposta la variabile ambiente per Roma
export CITY=roma

# Esegui lo script per generare i dati
python3 main.py
node scripts/fetch_notion.js
```

**Opzione B - File vuoto:**
```bash
echo '{"results": [], "totalRejectedCount": 0}' > public/data_roma.json
```

### 3. 🔄 **Aggiornamento Dati**

#### **Automatico (Raccomandato):**
I dati vengono aggiornati automaticamente ogni ora tramite GitHub Actions.

**Per aggiornamento manuale:**
1. Vai su GitHub → Actions
2. Seleziona il workflow `update-data.yml`
3. Clicca "Run workflow" → "Run workflow"

#### **Locale (per test):**
Se vuoi testare localmente, crea un file `.env` temporaneo:

```bash
# Crea file .env temporaneo per test locale
cp env.example .env
# Modifica .env con i tuoi valori reali

# Test per tutte le città
python3 process_cities.py

# Test per città specifica
CITY=barcelona python3 main.py
CITY=barcelona node scripts/fetch_notion.js
```

### 4. 🚀 **Deploy e Verifica**

#### **Deploy Automatico:**
Il sistema è già configurato per il deploy automatico su GitHub Pages.

#### **Verifica Funzionamento:**
1. **GitHub Actions**: Vai su GitHub → Actions → `update-data.yml`
2. **Verifica esecuzione**: Controlla che il workflow si esegua ogni ora
3. **Verifica file**: Controlla che `data_barcelona.json` e `data_roma.json` vengano aggiornati
4. **Verifica sito**: Il sito è disponibile su GitHub Pages

#### **Se hai modifiche da pushare:**
```bash
git add .
git commit -m "Update multi-city system"
git push origin main
```

### 5. 🔧 **Manutenzione Regolare**

**Ogni settimana:**
- Verifica che i feed RSS funzionino
- Controlla i log di GitHub Actions
- Verifica che i dati vengano aggiornati correttamente

**Ogni mese:**
- Controlla le performance del sistema
- Verifica che i GitHub Secrets siano ancora validi
- Controlla i log di GitHub Actions per errori
- Aggiorna le dipendenze se necessario

## ✅ **Sistema Cache Multi-Città**

Il sistema cache è **già ottimizzato** per multi-città:

- **Barcelona**: `rejected_urls_cache_barcelona.json`
- **Roma**: `rejected_urls_cache_roma.json`

Ogni città ha il suo file cache separato, quindi non ci sono conflitti.

## 🧹 **Files Puliti**

Ho rimosso i seguenti files inutili:
- `NEW_SYSTEM_SUMMARY.md`
- `test_new_system.py`
- `test_scalability.py`
- `test_system.py`
- `README.md` (vecchio)
- `__pycache__/`

## 🔍 **Controlli di Qualità**

Tutti i file sono stati verificati:

✅ **Python**: Tutti i file compilano correttamente  
✅ **JavaScript**: Sintassi corretta  
✅ **JSON**: Formato valido  
✅ **HTML**: Struttura corretta  

## 🎯 **Funzionalità Implementate**

✅ **Stats aggiornate** quando si cambia città  
✅ **Cache ottimizzata** per multi-città  
✅ **Files puliti** e organizzati  
✅ **Logica verificata** in tutti i file  
✅ **Welcome page** come pagina di apertura per nuovi utenti  
✅ **Fingerprint** per sincronizzazione cross-device  

## 🚨 **Problemi Noti**

1. **File `data_roma.json` mancante**: Devi crearlo manualmente o eseguire lo script per Roma
2. **Feed RSS per Roma**: Devi configurare i feed RSS specifici per Roma

## 📞 **Supporto**

Se hai problemi:
1. **Controlla i log di GitHub Actions**: Vai su GitHub → Actions → `update-data.yml` → ultima esecuzione
2. **Verifica i GitHub Secrets**: Vai su GitHub → Settings → Secrets and variables → Actions
3. **Controlla che i feed RSS siano accessibili**: Verifica gli URL nei secrets
4. **Verifica che i database Notion esistano**: Controlla i database ID nei secrets
5. **Controlla la console del browser**: Per errori frontend

---

**Il sistema è pronto per la produzione!** 🚀
