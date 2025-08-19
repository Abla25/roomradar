# 🚨 Sistema di Segnalazioni - Setup Guide

## 📋 Panoramica
Il sistema di segnalazioni permette agli utenti di segnalare annunci problematici cliccando sull'icona ⚠️ presente su ogni card. Le segnalazioni vengono inviate automaticamente a Google Forms senza richiedere login.

## 🎯 Funzionalità
- ✅ **Icona di segnalazione** su ogni card
- ✅ **Feedback visivo** (icona diventa rossa)
- ✅ **Invio automatico** a Google Forms
- ✅ **Zero login** richiesto
- ✅ **Dati completi** dell'annuncio segnalato

## 🔧 Setup Google Forms

### 1. Crea un nuovo Google Form
1. Vai su [Google Forms](https://forms.google.com)
2. Crea un nuovo form
3. Aggiungi i seguenti campi:

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| ID Annuncio | Testo breve | ID univoco dell'annuncio |
| Titolo Annuncio | Testo breve | Titolo dell'annuncio |
| Link Annuncio | Testo breve | URL dell'annuncio |
| Timestamp | Data/ora | Data e ora della segnalazione |

### 2. Ottieni l'ID del Form
1. Nel Google Form, clicca su "Invia"
2. Copia l'URL del form
3. Estrai l'ID dal URL: `https://docs.google.com/forms/d/e/FORM_ID/viewform`
4. Sostituisci `FORM_ID` nel codice JavaScript

### 3. Ottieni gli ID dei Campi
1. Apri il form in modalità modifica
2. Per ogni campo, clicca su "Risposte" → "Risposte individuali"
3. Invia una risposta di test
4. Nella risposta, trova gli ID dei campi (es. `entry.123456789`)
5. Sostituisci gli ID nel codice JavaScript

## 🔄 Integrazione con Notion (Opzionale)

### Setup Zapier
1. Crea un account su [Zapier](https://zapier.com)
2. Crea un nuovo Zap:
   - **Trigger**: Google Forms → Nuova risposta
   - **Action**: Notion → Crea database item
3. Configura i campi:
   - ID Annuncio → ID Annuncio
   - Titolo → Titolo
   - Link → Link
   - Timestamp → Data creazione

### Database Notion
Crea una nuova tabella in Notion con i campi:
- ID Annuncio (Testo)
- Titolo (Testo)
- Link (URL)
- Data Segnalazione (Data)
- Status (Selezione: Nuova/In Revisione/Risolta)

## 🎨 Personalizzazione

### Cambiare l'icona
Modifica la riga nel file `index.html`:
```html
<div class="report-icon" onclick="reportListing(...)">
  ⚠️  <!-- Cambia questa emoji -->
</div>
```

### Cambiare i colori
Modifica il CSS nel file `index.html`:
```css
.report-icon.reported {
  color: #dc3545; /* Rosso */
}

.report-icon.success {
  color: #28a745; /* Verde */
}

.report-icon.error {
  color: #ffc107; /* Giallo */
}
```

## 🚀 Test del Sistema

1. Apri la pagina in un browser
2. Clicca sull'icona ⚠️ su una card
3. Verifica che:
   - L'icona diventi rossa
   - Dopo 2 secondi diventi verde (successo)
   - La segnalazione appaia in Google Forms
   - Se configurato, la segnalazione appaia in Notion

## 📊 Monitoraggio

### Google Forms
- Vai su "Risposte" nel Google Form
- Visualizza tutte le segnalazioni ricevute
- Esporta i dati in Google Sheets se necessario

### Notion (se configurato)
- Visualizza la tabella delle segnalazioni
- Filtra per status
- Aggiungi note e aggiorna lo status

## 🔧 Risoluzione Problemi

### L'icona non cambia colore
- Verifica che il CSS sia caricato correttamente
- Controlla la console del browser per errori JavaScript

### Le segnalazioni non arrivano
- Verifica l'ID del form Google Forms
- Controlla gli ID dei campi
- Verifica che il form sia pubblico

### Errore CORS
- Il `mode: 'no-cors'` dovrebbe risolvere il problema
- Se persiste, verifica che l'URL del form sia corretto

## 📝 Note
- Il sistema funziona completamente lato client
- Nessun server da gestire
- Google Forms ha invii illimitati gratuiti
- Le segnalazioni sono anonime
