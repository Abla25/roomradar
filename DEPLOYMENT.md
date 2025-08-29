# 🚀 RoomRadar v2.0 - Deployment Guide

## Vercel Deployment

### Prerequisiti
- Account Vercel (gratuito)
- Repository GitHub aggiornato
- Firebase project configurato

### 1. Configurazione Vercel

#### Opzione A: Deploy Automatico (Raccomandato)
1. Vai su [vercel.com](https://vercel.com)
2. Clicca "New Project"
3. Importa il repository GitHub: `Abla25/roomradar`
4. Vercel rileverà automaticamente la configurazione

#### Opzione B: Deploy Manuale
```bash
# Installa Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

### 2. Configurazione Firebase

Il progetto è già configurato con Firebase. Le credenziali sono hardcoded in `index.html`:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyBdheYPtK3xPq-MkochYgM8CCJNF3AFPXM",
  authDomain: "roomradar-auth.firebaseapp.com",
  projectId: "roomradar-auth",
  storageBucket: "roomradar-auth.firebasestorage.app",
  messagingSenderId: "167307746619",
  appId: "1:167307746619:web:f7c42efa80049d86046b1e",
  measurementId: "G-3135P792LN"
};
```

### 3. Variabili d'Ambiente (Opzionale)

Se vuoi usare variabili d'ambiente invece di credenziali hardcoded:

1. In Vercel Dashboard → Project Settings → Environment Variables
2. Aggiungi:
   ```
   FIREBASE_API_KEY=AIzaSyBdheYPtK3xPq-MkochYgM8CCJNF3AFPXM
   FIREBASE_AUTH_DOMAIN=roomradar-auth.firebaseapp.com
   FIREBASE_PROJECT_ID=roomradar-auth
   FIREBASE_STORAGE_BUCKET=roomradar-auth.firebasestorage.app
   FIREBASE_MESSAGING_SENDER_ID=167307746619
   FIREBASE_APP_ID=1:167307746619:web:f7c42efa80049d86046b1e
   FIREBASE_MEASUREMENT_ID=G-3135P792LN
   ```

### 4. Configurazione Domini

#### Dominio Personalizzato (Opzionale)
1. Vercel Dashboard → Settings → Domains
2. Aggiungi il tuo dominio
3. Configura i DNS records come indicato

#### Dominio Vercel
Il progetto sarà disponibile su: `https://roomradar-[username].vercel.app`

### 5. Verifica Deployment

Dopo il deployment, verifica:

1. **Homepage**: `https://your-domain.vercel.app`
2. **Welcome page**: `https://your-domain.vercel.app/welcome`
3. **Firebase Auth**: Testa login/registrazione
4. **Responsive**: Testa su mobile/desktop

### 6. Monitoraggio

#### Vercel Analytics
- Vercel Dashboard → Analytics
- Monitora performance e errori

#### Firebase Analytics
- Firebase Console → Analytics
- Monitora autenticazioni e utilizzo

### 7. Troubleshooting

#### Problemi Comuni

**Errore 404 su refresh**
- ✅ Risolto con `vercel.json` routing

**Firebase non funziona**
- ✅ Credenziali già configurate
- ✅ Controlla console browser per errori

**Immagini non caricano**
- ✅ Controlla path in `public/` directory

**Autenticazione non funziona**
- ✅ Verifica Firebase project settings
- ✅ Controlla domain autorizzati in Firebase

### 8. Aggiornamenti

Per aggiornare il deployment:

```bash
# Push su GitHub
git add .
git commit -m "Update message"
git push origin main

# Vercel farà automaticamente il redeploy
```

### 9. File di Configurazione

#### vercel.json
- ✅ Routing per SPA
- ✅ Headers di sicurezza
- ✅ Cache optimization

#### package.json
- ✅ Scripts di deployment
- ✅ Dependencies configurate

### 10. Sicurezza

Il progetto include:
- ✅ Headers di sicurezza in `vercel.json`
- ✅ Firebase Authentication
- ✅ HTTPS automatico (Vercel)
- ✅ CSP headers

---

## 🎯 Deployment Checklist

- [ ] Repository GitHub aggiornato
- [ ] Vercel project creato
- [ ] Firebase configurato
- [ ] Dominio configurato (opzionale)
- [ ] Test funzionalità
- [ ] Test responsive
- [ ] Monitoraggio attivo

---

**Il progetto è pronto per il deployment! 🚀**
