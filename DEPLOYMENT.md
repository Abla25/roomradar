# 🚀 Deployment Automatico - Server Sempre Attivo

## 🎯 **Opzioni di Deployment**

### 1. **Vercel (Raccomandato) - Server Sempre Attivo**

#### Setup Automatico:
1. **Vai su [vercel.com](https://vercel.com)**
2. **Connetti il repository GitHub**
3. **Configura le variabili d'ambiente**:
   - `NOTION_API_KEY`
   - `NOTION_DATABASE_ID`
   - `OPENROUTER_API_KEY`
4. **Deploy automatico** ad ogni push

#### Vantaggi:
- ✅ **Sempre attivo** (serverless)
- ✅ **HTTPS automatico**
- ✅ **Deploy automatico** da GitHub
- ✅ **Gratuito** per uso personale

### 2. **Render - Server Sempre Attivo**

#### Setup:
1. **Vai su [render.com](https://render.com)**
2. **Crea un nuovo Web Service**
3. **Connetti il repository GitHub**
4. **Configura le variabili d'ambiente**
5. **Deploy automatico**

### 3. **Railway - Server Sempre Attivo**

#### Setup:
1. **Vai su [railway.app](https://railway.app)**
2. **Connetti il repository GitHub**
3. **Configura le variabili d'ambiente**
4. **Deploy automatico**

## 🔧 **Configurazione Post-Deploy**

### Aggiorna l'URL del Server nel Frontend:

```javascript
// In static/index.html, cambia:
const serverUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
  ? 'http://localhost:5000' 
  : 'https://your-vercel-app.vercel.app';  // ← Cambia questo URL
```

### Test del Deployment:

```bash
# Testa il server remoto
curl https://your-app.vercel.app/api/report
```

## 📊 **Monitoraggio**

### Verifica Funzionamento:
- ✅ **Server risponde**: `https://your-app.vercel.app/`
- ✅ **API funziona**: Testa una segnalazione
- ✅ **Database aggiornato**: Controlla il contatore in Notion
- ✅ **Log attivi**: Monitora i log del server

### Troubleshooting:
- **Errore 404**: Controlla l'URL del server nel frontend
- **Errore 500**: Verifica le variabili d'ambiente
- **CORS error**: Il server è configurato correttamente

## 🎉 **Risultato Finale**

Dopo il deployment:
- 🌐 **Frontend**: Accessibile da ovunque
- 🔄 **Server**: Sempre attivo e funzionante
- 📊 **Segnalazioni**: Aggiornate in tempo reale
- 🔒 **Sicuro**: HTTPS e token protetti
