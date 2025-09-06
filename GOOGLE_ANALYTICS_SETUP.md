# Google Analytics 4 Setup Guide per RoomRadar

## 📊 Panoramica

RoomRadar ora include un sistema completo di Google Analytics 4 che traccia:

- **Visite e page views** di tutti gli utenti (registrati e non registrati)
- **Selezione delle città** (Barcelona, Rome, London)
- **Tempo di permanenza** su ogni pagina
- **Interazioni utente** (click sui listing, filtri, preferiti)
- **Dati demografici** (quando disponibili)
- **Comportamento utenti** registrati vs anonimi

## 🚀 Come Configurare

### Passo 1: Ottieni il Measurement ID

1. Vai su [Google Analytics](https://analytics.google.com)
2. Se non hai ancora una proprietà per RoomRadar:
   - Clicca "Crea" → "Proprietà"
   - Nome proprietà: "RoomRadar"
   - Seleziona il fuso orario e la valuta
   - Clicca "Avanti"
3. Seleziona la tua proprietà RoomRadar
4. Vai su **Amministrazione** (icona ingranaggio in basso a sinistra)
5. Nella colonna "Proprietà", clicca su **Flussi di dati**
6. Clicca su **Aggiungi flusso** → **Web** (se non esiste già)
7. Inserisci:
   - URL del sito web: `https://roomradar.com` (o il tuo dominio)
   - Nome del flusso: "RoomRadar Website"
8. Clicca **Crea flusso**
9. **Copia il Measurement ID** (formato: `G-XXXXXXXXXX`)

### Passo 2: Configura il Measurement ID

Apri il file `assets/js/analytics-config.js` e sostituisci:

```javascript
export const GA_MEASUREMENT_ID = 'G-XXXXXXXXXX'; // Sostituisci con il tuo ID
```

Con il tuo Measurement ID reale:

```javascript
export const GA_MEASUREMENT_ID = 'G-ABC123DEF4'; // Esempio
```

### Passo 3: Verifica l'Integrazione

1. Apri il sito in locale o su produzione
2. Apri gli strumenti sviluppatore (F12)
3. Vai sulla tab **Console**
4. Dovresti vedere:
   ```
   📊 RoomRadar Analytics initialized for Homepage
   🔗 City analytics integration completed
   ```

5. Testa la selezione di una città - dovresti vedere:
   ```
   📊 City selection tracked: Barcelona
   ```

### Passo 4: Verifica in Google Analytics

1. Vai su Google Analytics
2. Seleziona la tua proprietà RoomRadar
3. Vai su **Report** → **Tempo reale**
4. Naviga sul tuo sito - dovresti vedere gli utenti attivi in tempo reale

## 📈 Cosa Viene Tracciato

### Eventi Automatici
- **page_view** - Ogni volta che un utente visita una pagina
- **scroll** - Quando l'utente scrolla (90% della pagina)
- **outbound_clicks** - Click su link esterni
- **file_downloads** - Download di file

### Eventi Personalizzati

#### Selezione Città
- `city_selected_dropdown` - Selezione città dal dropdown
- `first_city_selection` - Prima selezione città (nuovo utente)
- `city_search_started` - Avvio ricerca per città
- `city_change_initiated` - Cambio città
- `returning_user_with_city` - Utente di ritorno con città salvata

#### Contenuti
- `listings_loaded` - Caricamento listing per città
- `listings_displayed` - Numero di listing mostrati
- `listing_clicked` - Click su un singolo listing
- `filter_used` - Utilizzo filtri

#### Autenticazione
- `user_authenticated` - Utente loggato
- `user_sign_out` - Logout utente

#### Profilo e Preferiti
- `favorite_toggled` - Aggiunta/rimozione preferiti
- `favorite_listing_clicked` - Click listing dai preferiti
- `favorites_displayed` - Numero preferiti mostrati

### Proprietà Utente
- `user_type` - "authenticated" o "anonymous"
- `preferred_city` - Città preferita dell'utente
- `returning_user` - "yes" o "no"
- `selected_city` - Città attualmente selezionata

### Metriche Temporali
- `time_on_page` - Tempo trascorso su ogni pagina (ogni 30 secondi)
- `page_exit` - Tempo totale quando l'utente lascia la pagina
- `page_hidden/visible` - Cambio tab/finestra

## 🔍 Report Utili in Google Analytics

### 1. Popolarità Città
- Vai su **Report** → **Eventi**
- Filtra per evento `city_selected_dropdown`
- Guarda i parametri `selected_city`

### 2. Comportamento Utenti per Città
- Vai su **Esplora** → **Analisi per segmenti**
- Crea segmenti basati su `selected_city`
- Confronta metriche tra città

### 3. Funnel Conversione
- **Analisi per coorte** → Crea funnel:
  1. `page_view` (Homepage)
  2. `city_selected_dropdown`
  3. `listings_displayed`
  4. `listing_clicked`

### 4. Utenti Registrati vs Anonimi
- Filtra per `user_type`
- Confronta engagement e comportamento

### 5. Tempo di Permanenza
- **Report** → **Coinvolgimento** → **Pagine e schermate**
- Ordina per "Tempo medio di coinvolgimento"

## 🛠 Personalizzazioni Avanzate

### Aggiungere Eventi Personalizzati

```javascript
// In qualsiasi pagina, dopo che analytics è inizializzato
if (window.analytics) {
  window.analytics.trackCustomEvent('mio_evento_personalizzato', {
    event_category: 'Custom',
    event_label: 'valore_specifico',
    selected_city: 'Barcelona', // opzionale
    value: 123 // opzionale per valori numerici
  });
}
```

### Aggiungere Proprietà Utente

```javascript
if (window.analytics) {
  window.analytics.setUserProperty('lingua_preferita', 'italiano');
  window.analytics.setUserProperty('tipo_studente', 'erasmus');
}
```

## 🔒 Privacy e GDPR

L'integrazione è configurata per essere conforme al GDPR:

- ✅ **IP anonimizzati** automaticamente
- ✅ **Nessun dato personale** tracciato direttamente
- ✅ **Consenso cookie** gestito dal banner esistente
- ✅ **Dati demografici** opzionali (solo se disponibili)
- ✅ **Nessuna personalizzazione pubblicitaria**

## 🐛 Troubleshooting

### Problema: "Analytics not initialized"
**Soluzione**: Verifica che il Measurement ID sia configurato correttamente in `analytics-config.js`

### Problema: Eventi non appaiono in GA
**Soluzione**: 
1. Controlla la console per errori JavaScript
2. Verifica che il Measurement ID sia corretto
3. Aspetta 24-48 ore per i primi dati (GA ha un ritardo)

### Problema: "Failed to load analytics.js"
**Soluzione**: Verifica che i file siano nel percorso corretto e accessibili

### Problema: Dati duplicati
**Soluzione**: Assicurati di non avere altre implementazioni GA nella stessa pagina

## 📞 Supporto

Se hai problemi con l'implementazione:

1. Controlla la console del browser per errori
2. Verifica che tutti i file siano nella posizione corretta
3. Testa prima in locale, poi in produzione
4. Usa Google Analytics DebugView per debugging avanzato

## 🎯 Obiettivi Suggeriti

Configura questi obiettivi in Google Analytics per misurare il successo:

1. **Conversione Città**: `city_selected_dropdown`
2. **Engagement Listing**: `listing_clicked`
3. **Registrazione**: `user_authenticated`
4. **Fidelizzazione**: `returning_user_with_city`

---

**Nota**: Ricorda di aggiornare la Privacy Policy per includere l'uso di Google Analytics se non l'hai già fatto.
