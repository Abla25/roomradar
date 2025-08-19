# 🚀 Quick Start - Sistema di Segnalazioni

## ⚡ **Avvio Rapido**

### 1. **Configura le variabili d'ambiente**
```bash
cp env.example .env
# Modifica .env con i tuoi token Notion
```

### 2. **Avvia il server (Terminale 1)**
```bash
pip install -r requirements.txt
python server.py
```

### 3. **Apri il frontend (Terminale 2)**
```bash
# Opzione A: Server Python semplice
python -m http.server 8000
# Poi apri http://localhost:8000/static/

# Opzione B: Apri direttamente il file
open static/index.html
```

### 4. **Testa il sistema**
```bash
python test_server.py
```

## 🔧 **Risoluzione Problemi**

### ❌ **Errore 405 (Method Not Allowed)**
- **Causa**: Il server non è in esecuzione
- **Soluzione**: Avvia `python server.py`

### ❌ **Errore di connessione**
- **Causa**: Server non raggiungibile
- **Soluzione**: Verifica che sia in esecuzione su porta 5000

### ❌ **Token non validi**
- **Causa**: Variabili d'ambiente non configurate
- **Soluzione**: Controlla il file `.env`

## 🎯 **Come Funziona**

1. **Clicca** l'icona 🚩 accanto a un'inserzione
2. **Icona diventa rossa** ✅ per confermare
3. **Server aggiorna** automaticamente il database Notion
4. **Contatore incrementato** nel campo `Segnalazioni`

## 📊 **Verifica Funzionamento**

- ✅ Icona diventa rossa quando cliccata
- ✅ Console browser: "Segnalazione inviata con successo"
- ✅ Database Notion: Contatore `Segnalazioni` incrementato
- ✅ Log server: "Inserzione X aggiornata: 0 → 1 segnalazioni"
