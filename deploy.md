# 🚀 Deployment del Server di Segnalazioni

## 📋 **Opzioni di Deployment**

### 1. **Heroku** (Raccomandato)
```bash
# Installa Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Crea app
heroku create your-app-name

# Configura variabili d'ambiente
heroku config:set NOTION_API_KEY=your_token
heroku config:set NOTION_DATABASE_ID=your_db_id

# Deploy
git push heroku main
```

### 2. **Railway**
```bash
# Installa Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### 3. **Vercel**
```bash
# Installa Vercel CLI
npm install -g vercel

# Deploy
vercel
```

### 4. **DigitalOcean App Platform**
- Crea un nuovo app su DigitalOcean
- Connetti il repository GitHub
- Configura le variabili d'ambiente
- Deploy automatico

## 🔧 **Configurazione Post-Deploy**

1. **Aggiorna l'URL del server** nel frontend:
   ```javascript
   // In static/index.html, cambia:
   const response = await fetch('/api/report', {
   // In:
   const response = await fetch('https://your-app.herokuapp.com/api/report', {
   ```

2. **Verifica il funzionamento**:
   - Apri l'app nel browser
   - Prova a segnalare un'inserzione
   - Controlla i log del server
   - Verifica che il contatore nel database Notion si incrementi

## 🔒 **Sicurezza del Deployment**

- ✅ **HTTPS**: Tutti i provider supportano HTTPS automaticamente
- ✅ **Variabili d'ambiente**: I token sono protetti dalle variabili d'ambiente
- ✅ **CORS**: Configurato per accettare richieste dal frontend
- ✅ **Rate limiting**: Considera l'implementazione per evitare abusi

## 📊 **Monitoraggio**

- **Log del server**: Controlla i log per errori
- **Database Notion**: Verifica che le segnalazioni vengano registrate
- **Performance**: Monitora i tempi di risposta delle API
