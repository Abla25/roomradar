// Firebase Configuration for RoomRadar
// This file can be imported by any page that needs Firebase authentication

// Firebase configuration object
export const firebaseConfig = {
  apiKey: "AIzaSyBdheYPtK3xPq-MkochYgM8CCnJF3AFPXM",
  authDomain: "roomradar-auth.firebaseapp.com",
  projectId: "roomradar-auth",
  storageBucket: "roomradar-auth.firebasestorage.app",
  messagingSenderId: "167307746619",
  appId: "1:167307746619:web:8c8c8c8c8c8c8c8c8c8c8c"
};

// Cache for Firebase instances to prevent multiple initializations
let firebaseApp = null;
let firebaseAuth = null;

// Initialize Firebase function with performance optimizations
export async function initializeFirebase(pageName = 'Unknown Page') {
  try {
    // Check if Firebase is already initialized
    if (firebaseApp && firebaseAuth) {
      console.log(`⚡ Firebase already initialized, reusing instance for ${pageName}`);
      
      // Set up auth state listener if not already set
      if (!window.authStateListenerSet) {
        setupAuthStateListener(firebaseAuth, pageName);
        window.authStateListenerSet = true;
      }
      
      return { app: firebaseApp, auth: firebaseAuth };
    }

    console.log(`🔥 Initializing Firebase in ${pageName}...`);
    
    // Import Firebase modules dynamically with performance optimization
    const [{ initializeApp }, { getAuth, onAuthStateChanged }] = await Promise.all([
      import("https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js"),
      import("https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js")
    ]);
    
    // Initialize Firebase only once
    firebaseApp = initializeApp(firebaseConfig);
    firebaseAuth = getAuth(firebaseApp);
    
    console.log(`✅ Firebase initialized in ${pageName}`);
    
    // Make Firebase available globally
    window.firebase = { auth: firebaseAuth };
    window.auth = firebaseAuth;
    
    // Set up auth state listener
    setupAuthStateListener(firebaseAuth, pageName);
    window.authStateListenerSet = true;
    
    return { app: firebaseApp, auth: firebaseAuth };
  } catch (error) {
    console.error(`❌ Error initializing Firebase in ${pageName}:`, error);
    throw error;
  }
}

// Separate function for auth state listener to avoid multiple listeners
function setupAuthStateListener(auth, pageName) {
  // Remove existing listener if any
  if (window.currentAuthUnsubscribe) {
    window.currentAuthUnsubscribe();
  }
  
  window.currentAuthUnsubscribe = onAuthStateChanged(auth, (user) => {
    console.log(`🔄 Auth state changed in ${pageName}:`, user ? 'User logged in' : 'User logged out');
    
    if (user) {
      console.log(`✅ User is authenticated in ${pageName}`);
      
      // Update navbar to show profile icon
      updateNavbarAuth(true);
    } else {
      console.log(`❌ User is not authenticated in ${pageName}`);
      
      // Update navbar to show sign in button
      updateNavbarAuth(false);
    }
  });
}

// Optimized navbar update function
function updateNavbarAuth(isAuthenticated) {
  // Use requestAnimationFrame for smooth UI updates
  requestAnimationFrame(() => {
    if (isAuthenticated) {
      if (typeof window.showProfileIcon === 'function') {
        window.showProfileIcon();
      }
    } else {
      if (typeof window.showSignInButton === 'function') {
        window.showSignInButton();
      }
    }
  });
}

// Helper function to check if user is authenticated
export function isUserAuthenticated() {
  return window.auth && window.auth.currentUser;
}

// Helper function to get current user
export function getCurrentUser() {
  return window.auth ? window.auth.currentUser : null;
}

// Helper function to update navbar based on auth state
export function updateNavbarAuth(isAuthenticated) {
  if (isAuthenticated) {
    if (typeof window.showProfileIcon === 'function') {
      window.showProfileIcon();
    }
  } else {
    if (typeof window.showSignInButton === 'function') {
      window.showSignInButton();
    }
  }
}

// Performance monitoring
export function logPerformanceMetric(metric, value) {
  if (window.performance && window.performance.mark) {
    window.performance.mark(`${metric}-${Date.now()}`);
    console.log(`📊 Performance: ${metric} = ${value}ms`);
  }
}
