#!/usr/bin/env python3
"""
Server per gestire le segnalazioni e aggiornare automaticamente il database Notion
"""

import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

app = Flask(__name__)
CORS(app)  # Abilita CORS per richieste dal frontend

# Configurazione Notion
NOTION_TOKEN = os.getenv("NOTION_API_KEY")  # Usa la stessa variabile del workflow
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def find_listing_by_url(url: str):
    """Trova un'inserzione nel database Notion tramite URL"""
    try:
        query = {
            "filter": {
                "property": "Link",
                "url": {
                    "equals": url
                }
            }
        }
        
        response = requests.post(
            f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query",
            headers=NOTION_HEADERS,
            json=query
        )
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                return results[0]
        
        return None
        
    except Exception as e:
        print(f"Errore nella ricerca dell'inserzione: {e}")
        return None

def update_listing_reports(page_id: str) -> bool:
    """Incrementa il contatore delle segnalazioni per un'inserzione"""
    try:
        # Prima ottieni il valore attuale delle segnalazioni
        response = requests.get(
            f"https://api.notion.com/v1/pages/{page_id}",
            headers=NOTION_HEADERS
        )
        
        if response.status_code != 200:
            print(f"Errore nel recupero della pagina: {response.status_code}")
            return False
        
        page_data = response.json()
        current_reports = page_data.get("properties", {}).get("Segnalazioni", {}).get("number", 0)
        new_reports_count = current_reports + 1
        
        # Aggiorna il contatore delle segnalazioni
        update_data = {
            "properties": {
                "Segnalazioni": {
                    "number": new_reports_count
                }
            }
        }
        
        response = requests.patch(
            f"https://api.notion.com/v1/pages/{page_id}",
            headers=NOTION_HEADERS,
            json=update_data
        )
        
        if response.status_code == 200:
            print(f"Inserzione {page_id} aggiornata: {current_reports} → {new_reports_count} segnalazioni")
            return True
        else:
            print(f"Errore nell'aggiornamento: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Errore nell'aggiornamento dell'inserzione: {e}")
        return False

@app.route('/api/report', methods=['POST'])
def report_item():
    """Endpoint per ricevere segnalazioni dal frontend"""
    try:
        data = request.get_json()
        item_id = data.get('itemId')
        item_title = data.get('itemTitle')
        
        if not item_id:
            return jsonify({'error': 'ID inserzione mancante'}), 400
        
        # Cerca l'inserzione nel database
        listing = find_listing_by_url(item_id)
        
        if not listing:
            return jsonify({'error': 'Inserzione non trovata'}), 404
        
        # Incrementa il contatore delle segnalazioni
        page_id = listing["id"]
        success = update_listing_reports(page_id)
        
        if success:
            print(f"Segnalazione processata: {item_title} ({item_id})")
            return jsonify({'success': True, 'message': 'Segnalazione registrata'}), 200
        else:
            return jsonify({'error': 'Errore nell\'aggiornamento del database'}), 500
            
    except Exception as e:
        print(f"Errore nel processare la segnalazione: {e}")
        return jsonify({'error': 'Errore interno del server'}), 500

@app.route('/')
def serve_index():
    """Serve il file index.html"""
    return app.send_static_file('index.html')

@app.route('/public/<path:filename>')
def serve_public(filename):
    """Serve i file dalla cartella public"""
    return app.send_static_file(f'../public/{filename}')

if __name__ == '__main__':
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("❌ Configura le variabili d'ambiente NOTION_API_KEY e NOTION_DATABASE_ID")
        exit(1)
    
    print("🚀 Server avviato su http://localhost:5000")
    print("📊 Le segnalazioni verranno aggiornate automaticamente nel database Notion")
    
    # In produzione, usa la porta fornita dall'ambiente
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
