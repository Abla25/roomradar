// Favorites Management for RoomRadar
// Handles saving, removing, and displaying favorite listings

import { getFirestore, doc, getDoc, updateDoc, setDoc, arrayUnion, arrayRemove } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

// Cache per i preferiti dell'utente corrente
let userFavorites = new Set();
let favoritesLoaded = false;

// Inizializza il sistema preferiti
export async function initializeFavorites(auth) {
  if (!auth || !auth.currentUser) {
    console.log('❌ User not authenticated, favorites disabled');
    return;
  }

  try {
    console.log('💖 Initializing favorites system...');
    const db = getFirestore();
    const userDocRef = doc(db, 'users', auth.currentUser.uid);
    const userDoc = await getDoc(userDocRef);
    
    if (userDoc.exists()) {
      const userData = userDoc.data();
      userFavorites = new Set(userData.favorites || []);
      favoritesLoaded = true;
      console.log(`✅ Favorites loaded: ${userFavorites.size} items`);
    } else {
      // Crea documento utente se non esiste
      await setDoc(userDocRef, { favorites: [] });
      userFavorites = new Set();
      favoritesLoaded = true;
      console.log('✅ New user favorites initialized');
    }
  } catch (error) {
    console.error('❌ Error loading favorites:', error);
  }
}

// Salva un annuncio nei preferiti
export async function addToFavorites(auth, listingId, listingData) {
  if (!auth || !auth.currentUser) {
    console.log('❌ User not authenticated, cannot add to favorites');
    return false;
  }

  try {
    console.log(`💖 Adding listing ${listingId} to favorites...`);
    console.log('📋 Listing data received:', listingData);
    
    const db = getFirestore();
    const userDocRef = doc(db, 'users', auth.currentUser.uid);
    
    // Aggiungi ai preferiti
    await updateDoc(userDocRef, {
      favorites: arrayUnion(listingId)
    });
    
    // Aggiorna cache locale
    userFavorites.add(listingId);
    
    // Salva sempre il riferimento all'annuncio
    if (listingData && Object.keys(listingData).length > 0) {
      await saveListingData(listingId, listingData);
    } else {
      console.log('⚠️ No listing data provided, creating minimal reference');
      // Crea riferimento minimo se non disponibili
      const minimalData = {
        id: listingId,
        city: 'barcelona', // default
        savedAt: new Date().toISOString()
      };
      await saveListingData(listingId, minimalData);
    }
    
    console.log(`✅ Added to favorites: ${listingId}`);
    return true;
  } catch (error) {
    console.error('❌ Error adding to favorites:', error);
    return false;
  }
}

// Rimuovi un annuncio dai preferiti
export async function removeFromFavorites(auth, listingId) {
  if (!auth || !auth.currentUser) {
    console.log('❌ User not authenticated, cannot remove from favorites');
    return false;
  }

  try {
    console.log(`💔 Removing listing ${listingId} from favorites...`);
    const db = getFirestore();
    const userDocRef = doc(db, 'users', auth.currentUser.uid);
    
    // Rimuovi dai preferiti
    await updateDoc(userDocRef, {
      favorites: arrayRemove(listingId)
    });
    
    // Aggiorna cache locale
    userFavorites.delete(listingId);
    
    console.log(`✅ Removed from favorites: ${listingId}`);
    return true;
  } catch (error) {
    console.error('❌ Error removing from favorites:', error);
    return false;
  }
}

// Controlla se un annuncio è nei preferiti
export function isFavorite(listingId) {
  return userFavorites.has(listingId);
}

// Ottieni tutti i preferiti dell'utente
export function getFavorites() {
  return Array.from(userFavorites);
}

// Controlla se i preferiti sono caricati
export function areFavoritesLoaded() {
  return favoritesLoaded;
}

// Salva i dati dell'annuncio per accesso offline
async function saveListingData(listingId, listingData) {
  try {
    console.log('💾 Saving listing reference:', { listingId, listingData });
    
    const db = getFirestore();
    const listingDocRef = doc(db, 'favorite_listings', listingId);
    
    // Salva dati più completi per il profilo
    const referenceData = {
      id: listingId,
      city: listingData?.city || 'barcelona',
      title: listingData?.title || 'Untitled',
      price: listingData?.price || 'N/A',
      zone: listingData?.zone || 'N/A',
      zoneMacro: listingData?.zoneMacro || listingData?.zone || 'N/A',
      imageUrl: listingData?.imageUrl || listingData?.image || '',
      link: listingData?.link || listingData?.url || '',
      description: listingData?.description || listingData?.overview || '',
      overview: listingData?.overview || listingData?.description || '',
      reliability: listingData?.reliability || 'N/A',
      reliabilityReason: listingData?.reliabilityReason || '',
      dateAdded: listingData?.dateAdded || new Date().toISOString(),
      savedAt: new Date().toISOString()
    };
    
    console.log('💾 Reference data to save:', referenceData);
    
    await setDoc(listingDocRef, referenceData);
    console.log(`💾 Saved listing reference for: ${listingId}`);
    
    // Verifica che i dati siano stati salvati
    const savedDoc = await getDoc(listingDocRef);
    if (savedDoc.exists()) {
      console.log('✅ Reference successfully saved and verified:', savedDoc.data());
    } else {
      console.error('❌ Reference was not saved properly');
    }
  } catch (error) {
    console.error('❌ Error saving listing reference:', error);
  }
}

// Carica i dati di un annuncio preferito
export async function getFavoriteListingData(listingId) {
  try {
    console.log('🔍 Loading reference for listing:', listingId);
    
    const db = getFirestore();
    const listingDocRef = doc(db, 'favorite_listings', listingId);
    const listingDoc = await getDoc(listingDocRef);
    
    if (listingDoc.exists()) {
      const savedData = listingDoc.data();
      console.log('📋 Saved data for listing', listingId, ':', savedData);
      
      // Se abbiamo dati salvati completi, usali direttamente
      if (savedData.title && savedData.title !== 'Untitled') {
        console.log('✅ Using saved data for listing:', listingId);
        return savedData;
      }
      
      // Altrimenti, prova a recuperare dal JSON come fallback
      const city = savedData.city || 'barcelona';
      const fullData = await getListingDataFromJSON(listingId, city);
      
      if (fullData) {
        console.log('✅ Full data retrieved from JSON for listing:', listingId, fullData);
        return fullData;
      } else {
        console.log('⚠️ Using minimal saved data for listing:', listingId);
        return savedData;
      }
    } else {
      console.log('❌ No reference found for listing:', listingId);
      return null;
    }
  } catch (error) {
    console.error('❌ Error loading listing data:', error);
    return null;
  }
}

async function getListingDataFromJSON(listingId, city) {
  try {
    console.log('🔍 Fetching data from JSON for:', { listingId, city });
    
    // Carica il JSON della città
    const response = await fetch(`/public/data_${city}.json`);
    if (!response.ok) {
      console.error('❌ Failed to fetch JSON for city:', city);
      return null;
    }
    
    const data = await response.json();
    console.log('📋 JSON data loaded for city:', city, 'with', data.results?.length, 'listings');
    
    // Cerca l'annuncio per ID
    const listing = data.results?.find(l => l.id === listingId);
    
    if (listing) {
      console.log('✅ Found listing in JSON:', listing);
      
      // Controlla se l'annuncio è scaduto o necessita verifica
      const status = listing.status || listing.verification_status || 'active';
      const isExpired = status === 'expired' || status === 'Expired';
      const needsVerification = status === 'verification_needed' || status === 'Verification Needed';
      
      if (isExpired) {
        console.log('⚠️ Listing is expired:', listingId);
        return { ...listing, _isExpired: true };
      }
      
      if (needsVerification) {
        console.log('⚠️ Listing needs verification:', listingId);
        return { ...listing, _needsVerification: true };
      }
      
      return listing;
    } else {
      console.log('❌ Listing not found in JSON:', listingId);
      return null;
    }
  } catch (error) {
    console.error('❌ Error fetching from JSON:', error);
    return null;
  }
}

// Carica tutti i dati degli annunci preferiti
export async function getAllFavoriteListingsData() {
  const favorites = getFavorites();
  console.log('🔍 Getting data for favorites:', favorites);
  const listingsData = [];
  const expiredListings = [];
  const unverifiedListings = [];
  
  for (const listingId of favorites) {
    console.log('🔍 Loading data for listing:', listingId);
    const data = await getFavoriteListingData(listingId);
    console.log('📋 Data for listing', listingId, ':', data);
    
    if (data) {
      // Controlla se l'annuncio è scaduto o necessita verifica
      if (data._isExpired) {
        console.log('⚠️ Skipping expired listing:', listingId);
        expiredListings.push(listingId);
        continue; // Salta questo annuncio
      }
      
      if (data._needsVerification) {
        console.log('⚠️ Skipping unverified listing:', listingId);
        unverifiedListings.push(listingId);
        continue; // Salta questo annuncio
      }
      
      listingsData.push(data);
    } else {
      console.log('❌ No data found for listing:', listingId);
    }
  }
  
  // Rimuovi automaticamente gli annunci scaduti/non verificati dai favorites
  if (expiredListings.length > 0 || unverifiedListings.length > 0) {
    console.log('🧹 Cleaning up expired/unverified favorites:', { expiredListings, unverifiedListings });
    
    // Rimuovi gli annunci scaduti/non verificati dai favorites
    const allProblematicListings = [...expiredListings, ...unverifiedListings];
    for (const listingId of allProblematicListings) {
      await removeFromFavorites(window.auth || window.firebase?.auth, listingId);
      console.log('🗑️ Removed problematic listing from favorites:', listingId);
    }
  }
  
  console.log('📋 All valid listings data:', listingsData);
  return listingsData;
}

// Aggiorna l'UI dei pulsanti preferiti
export function updateFavoriteButtons() {
  const favoriteButtons = document.querySelectorAll('[data-favorite-btn]');
  
  favoriteButtons.forEach(button => {
    const listingId = button.getAttribute('data-listing-id');
    if (!listingId) return;
    
    const isFav = isFavorite(listingId);
    
    // Update icon
    const icon = button.querySelector('.favorite-icon');
    if (icon) {
      icon.innerHTML = isFav ? 
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>' :
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>';
    }
    
    // Update title attribute for accessibility
    button.title = isFav ? 'Remove from favorites' : 'Add to favorites';
    
    // Update tooltip
    button.setAttribute('data-tooltip', isFav ? 'Remove from favorites' : 'Add to favorites');
    
    // Aggiorna classe CSS
    button.classList.toggle('favorited', isFav);
  });
}

// Gestisce il click su un pulsante preferiti
export async function handleFavoriteClick(auth, listingId, listingData) {
  console.log('💖 handleFavoriteClick called with:', { auth, listingId, listingData });
  
  // Check authentication using multiple sources
  let currentAuth = auth;
  let currentUser = null;
  
  // Try different ways to get the auth object
  if (currentAuth && currentAuth.currentUser) {
    currentUser = currentAuth.currentUser;
    console.log('✅ Found user from passed auth object');
  } else if (window.auth && window.auth.currentUser) {
    currentAuth = window.auth;
    currentUser = window.auth.currentUser;
    console.log('✅ Found user from window.auth');
  } else if (window.firebase && window.firebase.auth && window.firebase.auth.currentUser) {
    currentAuth = window.firebase.auth;
    currentUser = window.firebase.auth.currentUser;
    console.log('✅ Found user from window.firebase.auth');
  } else if (window.currentUser) {
    // User is authenticated but auth object not available globally
    // We need to get the auth object from the Firebase app
    console.log('✅ Found user from window.currentUser, getting auth object...');
    try {
      // Import Firebase to get the auth object
      const { getAuth } = await import("https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js");
      const { getApp } = await import("https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js");
      
      const app = getApp();
      currentAuth = getAuth(app);
      currentUser = window.currentUser;
      console.log('✅ Retrieved auth object from Firebase app');
    } catch (error) {
      console.error('❌ Error getting auth object:', error);
    }
  } else {
    console.log('❌ No auth object found, checking global variables...');
    console.log('window.auth:', window.auth);
    console.log('window.firebase:', window.firebase);
    console.log('window.currentUser:', window.currentUser);
  }
  
  if (!currentUser) {
    console.log('❌ User not authenticated, showing login modal...');
    // Show login modal
    if (typeof window.showAuthModal === 'function') {
      window.showAuthModal();
    } else {
      // Fallback: redirect to homepage for login
      window.location.href = '/';
    }
    return;
  }

  const isFav = isFavorite(listingId);
  
  if (isFav) {
    await removeFromFavorites(currentAuth, listingId);
  } else {
    await addToFavorites(currentAuth, listingId, listingData);
  }
  
  // Update UI
  updateFavoriteButtons();
}

// Esporta funzioni globali per compatibilità
window.initializeFavorites = initializeFavorites;
window.addToFavorites = addToFavorites;
window.removeFromFavorites = removeFromFavorites;
window.isFavorite = isFavorite;
window.getFavorites = getFavorites;
window.handleFavoriteClick = handleFavoriteClick;
window.updateFavoriteButtons = updateFavoriteButtons;
