#!/usr/bin/env python3
"""
Test del server di segnalazioni
"""

import requests
import json

def test_server():
    """Testa il server di segnalazioni"""
    
    # Test 1: Verifica che il server risponda
    try:
        response = requests.get('http://localhost:5000/')
        print(f"✅ Server risponde: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server non raggiungibile. Assicurati che sia in esecuzione con: python server.py")
        return False
    
    # Test 2: Verifica endpoint di segnalazione
    test_data = {
        "itemId": "https://www.facebook.com/groups/test/posts/123456789",
        "itemTitle": "Test Inserzione",
        "timestamp": "2025-01-20T10:30:00.000Z",
        "userAgent": "Test Browser"
    }
    
    try:
        response = requests.post('http://localhost:5000/api/report', 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        print(f"✅ Endpoint /api/report risponde: {response.status_code}")
        if response.status_code == 404:
            print("ℹ️  Inserzione non trovata nel database (normale per test)")
        elif response.status_code == 200:
            print("✅ Segnalazione processata con successo")
        else:
            print(f"⚠️  Risposta inaspettata: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Endpoint non raggiungibile")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Test del server di segnalazioni...")
    success = test_server()
    if success:
        print("✅ Tutti i test completati")
    else:
        print("❌ Test falliti")
