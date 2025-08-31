# Sistema di Segnalazioni - RoomRadar

## 🎯 Panoramica

Il sistema di segnalazioni permette agli utenti registrati di segnalare annunci problematici (spam, truffe, link non funzionanti, ecc.) direttamente dall'interfaccia. Le segnalazioni vengono salvate su Firebase e inviate automaticamente via email e a Notion.

## 🏗️ Architettura

### Frontend
- **Pulsante segnalazione**: Icona triangolare accanto al pulsante preferiti
- **Modal di segnalazione**: Form con selezione tipo e descrizione
- **Visibilità condizionale**: Solo per utenti registrati

### Backend
- **Firebase Firestore**: Database principale per le segnalazioni
- **Firebase Functions**: Gestione email e integrazione Notion
- **Email**: Notifiche automatiche via Gmail SMTP
- **Notion**: Sincronizzazione automatica con database

## 📁 Struttura Dati

### Collezione `reports` (Firestore)
```json
{
  "reportId": "auto-generated",
  "userId": "user123",
  "userEmail": "user@example.com",
  "userDisplayName": "Mario Rossi",
  "listingId": "listing456",
  "listingUrl": "https://facebook.com/listing456",
  "listingTitle": "Stanza in centro",
  "listingPrice": "€500/mese",
  "listingZone": "Eixample",
  "reportType": "spam|scam|broken_link|owner_removal|inappropriate|duplicate|other",
  "description": "Motivazione dettagliata...",
  "status": "pending|reviewed|resolved",
  "createdAt": "2024-01-01T10:00:00Z",
  "reviewedAt": null,
  "reviewerNotes": null,
  "notionPageId": "notion-page-id",
  "notionSynced": true
}
```

## 🔧 Tipi di Segnalazione

1. **Spam**: Contenuto non pertinente o pubblicità
2. **Scam/Fraud**: Truffe o annunci falsi
3. **Broken Link**: Link non funzionante
4. **Owner Removal**: Richiesta di rimozione dal proprietario
5. **Inappropriate Content**: Contenuto inappropriato
6. **Duplicate Listing**: Annuncio duplicato
7. **Other**: Altri motivi

## 🚀 Implementazione

### 1. Frontend - Pulsante Segnalazione

**Posizione**: Accanto al pulsante preferiti su ogni annuncio
**Visibilità**: Solo per utenti registrati
**Stile**: Icona triangolare con tooltip "Report listing"

```html
<button class="btn btn-secondary report-btn" 
        data-report-btn 
        data-listing-id="${listingId}" 
        data-tooltip="Report listing" 
        onclick="handleReportClick(window.auth, '${listingId}')" 
        title="Report listing">
  <span class="report-icon">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  </span>
</button>
```

### 2. Modal di Segnalazione

**Contenuto**:
- Selezione tipo di segnalazione (dropdown)
- Campo testo per descrizione aggiuntiva
- Pulsanti "Cancel" e "Submit Report"

**Validazione**:
- Tipo di segnalazione obbligatorio
- Descrizione opzionale ma consigliata

### 3. Backend - Firebase Functions

#### Email Function (`sendReportEmail`)
- **Trigger**: Creazione documento in collezione `reports`
- **Azione**: Invia email HTML con dettagli segnalazione
- **Destinatario**: Email admin configurata
- **Contenuto**: Dettagli segnalazione + link Firebase Console

#### Notion Function (`sendToNotion`)
- **Trigger**: Creazione documento in collezione `reports`
- **Azione**: Crea pagina in database Notion
- **Sincronizzazione**: Aggiorna Firestore con ID pagina Notion

#### Status Update Function (`updateNotionStatus`)
- **Trigger**: Aggiornamento documento in collezione `reports`
- **Azione**: Aggiorna status in Notion quando cambia in Firestore

## 📧 Configurazione Email

### Gmail SMTP Setup
1. **Abilita 2FA** sul tuo account Gmail
2. **Genera password app** per l'applicazione
3. **Configura Firebase Functions**:

```bash
firebase functions:config:set email.user="your-email@gmail.com"
firebase functions:config:set email.pass="your-app-password"
firebase functions:config:set email.admin="admin@yourdomain.com"
```

### Template Email
- **Oggetto**: `🚨 New Report: {type} - RoomRadar`
- **Contenuto**: HTML con dettagli segnalazione
- **Link**: Diretto a Firebase Console

## 📝 Configurazione Notion

### Database Setup
1. **Crea database** in Notion con queste proprietà:
   - `Title` (Title)
   - `Report Type` (Select)
   - `Status` (Select: Pending, Reviewed, Resolved)
   - `User` (Rich Text)
   - `Listing URL` (URL)
   - `Created` (Date)
   - `Description` (Rich Text)

2. **Configura Firebase Functions**:
```bash
firebase functions:config:set notion.token="your-notion-integration-token"
firebase functions:config:set notion.database_id="your-database-id"
```

### Notion Integration
1. **Crea integrazione** su https://www.notion.so/my-integrations
2. **Condividi database** con l'integrazione
3. **Copia token** e database ID

## 🔒 Sicurezza

### Regole Firestore
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Utenti possono creare solo le proprie segnalazioni
    match /reports/{reportId} {
      allow create: if request.auth != null && 
                   request.auth.uid == resource.data.userId;
      allow read: if request.auth != null && 
                 (request.auth.uid == resource.data.userId || 
                  isAdmin(request.auth.uid));
      allow update: if request.auth != null && isAdmin(request.auth.uid);
    }
  }
}
```

### Validazione Frontend
- Solo utenti registrati possono segnalare
- Validazione tipo segnalazione obbligatorio
- Rate limiting (max 5 segnalazioni/ora per utente)

## 📊 Dashboard Admin

### Firebase Console
- **Percorso**: Firestore → Collezione `reports`
- **Funzionalità**: Visualizza, modifica status, aggiungi note
- **Filtri**: Per tipo, status, data

### Notion Database
- **Vista**: Database con tutte le segnalazioni
- **Filtri**: Per tipo, status, utente
- **Sincronizzazione**: Automatica con Firestore

## 🚀 Deployment

### 1. Installa dipendenze
```bash
cd functions
npm install
```

### 2. Configura variabili
```bash
firebase functions:config:set email.user="your-email@gmail.com"
firebase functions:config:set email.pass="your-app-password"
firebase functions:config:set email.admin="admin@yourdomain.com"
firebase functions:config:set notion.token="your-notion-token"
firebase functions:config:set notion.database_id="your-database-id"
```

### 3. Deploy
```bash
firebase deploy --only functions
```

## 🧪 Testing

### Test Manuali
1. **Login utente** e verifica visibilità pulsante segnalazione
2. **Clicca segnalazione** e verifica apertura modal
3. **Compila form** e invia segnalazione
4. **Verifica email** ricevuta
5. **Verifica Notion** sincronizzazione
6. **Test senza login** (pulsante nascosto)

### Test Automatici (da implementare)
```javascript
describe('Reports System', () => {
  test('should show report button only for logged users', () => {
    // Test implementation
  });
  
  test('should create report in Firestore', () => {
    // Test implementation
  });
  
  test('should send email notification', () => {
    // Test implementation
  });
});
```

## 📈 Metriche e Analytics

### Dati da Tracciare
- Numero segnalazioni per tipo
- Tempo medio di risposta
- Segnalazioni per utente
- Annunci più segnalati

### Implementazione
```javascript
// Esempio tracking
function trackReportAction(action, reportType) {
  if (typeof gtag !== 'undefined') {
    gtag('event', 'report_action', {
      'action': action,
      'report_type': reportType,
      'user_id': auth.currentUser?.uid
    });
  }
}
```

## 🔮 Estensioni Future

### 1. Dashboard Web
- Interfaccia web per gestione segnalazioni
- Statistiche e analytics
- Bulk actions

### 2. Notifiche Push
- Notifiche push per nuove segnalazioni
- Alert per segnalazioni urgenti

### 3. Auto-moderation
- AI per rilevamento automatico spam
- Filtri automatici per contenuto inappropriato

### 4. Integrazione Slack
- Notifiche su canale Slack
- Comandi slash per gestione

## 🐛 Troubleshooting

### Problema: Email non inviate
**Soluzione**: Verifica configurazione Gmail SMTP e password app

### Problema: Notion non sincronizza
**Soluzione**: Verifica token integrazione e permessi database

### Problema: Pulsante segnalazione non visibile
**Soluzione**: Verifica stato autenticazione utente

### Problema: Modal non si apre
**Soluzione**: Verifica import modulo reports.js

## 📝 Note di Implementazione

### Considerazioni Tecniche
- **Performance**: Firebase Functions hanno timeout di 60s
- **Rate Limiting**: Gmail ha limite di 500 email/giorno
- **Notion API**: Limite di 3 richieste/secondo

### Costi
- **Firebase Functions**: Gratuito fino a 125K invocazioni/mese
- **Firestore**: Gratuito fino a 50K letture/scritture/mese
- **Email**: Gratuito con Gmail SMTP
- **Notion**: API gratuita

### Manutenzione
- **Monitoraggio**: Log Firebase Functions
- **Backup**: Export periodico dati Firestore
- **Aggiornamenti**: Mantieni dipendenze aggiornate
