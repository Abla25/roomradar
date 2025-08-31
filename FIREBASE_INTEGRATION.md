# Firebase Integration Guide

## Overview
Tutte le pagine di RoomRadar ora hanno Firebase integrato per mantenere lo stato di autenticazione coerente.

## Pagine Aggiornate

### ✅ Homepage (`index.html`)
- Firebase già integrato
- Gestione completa dell'autenticazione
- Listings dinamici basati su stato utente

### ✅ Profile Page (`profile.html`)
- Firebase integrato con Firestore
- Caricamento dati utente reali
- Sign out funzionante

### ✅ FAQ Page (`faq.html`)
- Firebase integrato
- Navbar aggiornata dinamicamente
- Stato autenticazione sincronizzato

### ✅ How It Works Page (`how-it-works.html`)
- Firebase integrato
- Navbar aggiornata dinamicamente
- Stato autenticazione sincronizzato

## Per Future Pagine

### Opzione 1: Usa il Template
```bash
# Copia il template
cp assets/templates/page-template.html your-new-page.html

# Modifica il template:
# 1. Cambia PAGE_TITLE
# 2. Cambia PAGE_DESCRIPTION  
# 3. Cambia PAGE_NAME
# 4. Aggiungi il tuo contenuto
```

### Opzione 2: Integrazione Manuale
Aggiungi questo codice alla tua pagina:

```html
<!-- Firebase SDK -->
<script type="module">
  // Import Firebase configuration
  import { initializeFirebase } from './assets/js/firebase-config.js';
  
  // Initialize Firebase for this page
  initializeFirebase('Your Page Name')
    .then(() => {
      console.log('✅ Firebase initialized successfully');
    })
    .catch((error) => {
      console.error('❌ Failed to initialize Firebase:', error);
    });
</script>
```

E queste funzioni JavaScript:

```javascript
// Profile icon functions
function showProfileIcon() {
  const signInBtn = document.getElementById('navbar-signin-btn');
  const profileIcon = document.getElementById('navbar-profile-icon');
  const mobileSignInBtn = document.getElementById('mobile-signin-btn');
  const mobileProfileIcon = document.getElementById('mobile-profile-icon');
  
  if (signInBtn && profileIcon) {
    signInBtn.style.display = 'none';
    profileIcon.style.display = 'flex';
  }
  
  if (mobileSignInBtn && mobileProfileIcon) {
    mobileSignInBtn.style.display = 'none';
    mobileProfileIcon.style.display = 'flex';
  }
}

function showSignInButton() {
  const signInBtn = document.getElementById('navbar-signin-btn');
  const profileIcon = document.getElementById('navbar-profile-icon');
  const mobileSignInBtn = document.getElementById('mobile-signin-btn');
  const mobileProfileIcon = document.getElementById('mobile-profile-icon');
  
  if (signInBtn && profileIcon) {
    signInBtn.style.display = 'flex';
    profileIcon.style.display = 'none';
  }
  
  if (mobileSignInBtn && mobileProfileIcon) {
    mobileSignInBtn.style.display = 'flex';
    mobileProfileIcon.style.display = 'none';
  }
}

function toggleProfileMenu() {
  window.location.href = '/profile.html';
}

function checkUserAuthStatus() {
  if (window.auth && window.auth.currentUser) {
    showProfileIcon();
  } else {
    showSignInButton();
  }
}

// Make functions globally available
window.showProfileIcon = showProfileIcon;
window.showSignInButton = showSignInButton;
window.toggleProfileMenu = toggleProfileMenu;
window.checkUserAuthStatus = checkUserAuthStatus;
```

## Funzionalità Disponibili

### 🔥 Firebase Functions
- `window.auth` - Firebase Auth instance
- `window.firebase.auth` - Firebase Auth instance
- `window.auth.currentUser` - Current authenticated user

### 🎯 Helper Functions
- `isUserAuthenticated()` - Check if user is logged in
- `getCurrentUser()` - Get current user object
- `updateNavbarAuth()` - Update navbar based on auth state

### 🎨 UI Functions
- `showProfileIcon()` - Show profile icon in navbar
- `showSignInButton()` - Show sign in button in navbar
- `toggleProfileMenu()` - Handle profile menu click
- `checkUserAuthStatus()` - Check and update UI based on auth

## Test Flow

### 1. Login Flow
1. Vai alla homepage
2. Fai login con Google
3. Naviga tra le pagine
4. Verifica che l'icona profilo sia visibile ovunque

### 2. Logout Flow
1. Vai alla pagina profile
2. Clicca "Sign Out"
3. Conferma il logout
4. Verifica che torni alla homepage con pulsante "Sign In"
5. Naviga tra le pagine
6. Verifica che il pulsante "Sign In" sia visibile ovunque

### 3. Limited Access Flow
1. Senza essere loggato, vai alla homepage
2. Verifica che mostri solo 15 listings
3. Naviga tra le pagine
4. Verifica che il pulsante "Sign In" sia visibile ovunque

## Logging

Ogni pagina ha logging dettagliato:
- 🔥 Firebase initialization
- 🔄 Auth state changes
- ✅ User authentication status
- 📱 Navbar element updates

## Troubleshooting

### Problema: Navbar non si aggiorna
**Soluzione:** Verifica che `checkUserAuthStatus()` sia chiamata dopo il caricamento della navbar

### Problema: Firebase non disponibile
**Soluzione:** Verifica che il modulo Firebase sia caricato correttamente

### Problema: Funzioni non globali
**Soluzione:** Assicurati che le funzioni siano assegnate a `window.functionName`

## File di Configurazione

- `assets/js/firebase-config.js` - Configurazione Firebase riutilizzabile
- `assets/templates/page-template.html` - Template per nuove pagine
- `assets/navbar.html` - Navbar modulare
- `assets/footer.html` - Footer modulare

