#!/usr/bin/env python3
"""
Script per censurare tutti i dati esistenti nel database Notion

Questo script:
1. Legge tutti i record dal database Notion usando i secrets di GitHub
2. Censura le descrizioni originali
3. Aggiorna i record nel database
4. Aggiorna il file data.json
5. Si auto-cancella dopo l'esecuzione

ATTENZIONE: Questo script modifica permanentemente i dati nel database!
"""

import os
import json
import requests
from datetime import datetime
from censorship import censor_sensitive_data, has_sensitive_data, get_censorship_stats

# Configurazione - usa i secrets di GitHub
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

if not NOTION_API_KEY or not NOTION_DATABASE_ID:
    print("❌ Errore: Variabili d'ambiente NOTION_API_KEY e NOTION_DATABASE_ID richieste")
    print("   Assicurati che i secrets siano configurati su GitHub")
    exit(1)

NOTION_API_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_API_VERSION
}

def get_all_notion_records():
    """Recupera tutti i record dal database Notion"""
    print("📥 Recuperando tutti i record dal database Notion...")
    
    all_records = []
    start_cursor = None
    
    while True:
        url = f"{BASE_URL}/databases/{NOTION_DATABASE_ID}/query"
        
        payload = {
            "page_size": 100,
            "filter": {
                "property": "Status",
                "select": {
                    "equals": "Attivo"
                }
            }
        }
        
        if start_cursor:
            payload["start_cursor"] = start_cursor
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            records = data.get("results", [])
            all_records.extend(records)
            
            print(f"📄 Recuperati {len(records)} record (totale: {len(all_records)})")
            
            # Controlla se ci sono più pagine
            if not data.get("has_more"):
                break
                
            start_cursor = data.get("next_cursor")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Errore nel recupero record: {e}")
            break
    
    print(f"✅ Recuperati {len(all_records)} record totali")
    return all_records

def update_notion_record(page_id, censored_description):
    """Aggiorna un record Notion con la descrizione censurata"""
    url = f"{BASE_URL}/pages/{page_id}"
    
    payload = {
        "properties": {
            "Descrizione_originale": {
                "rich_text": [
                    {
                        "text": {
                            "content": censored_description
                        }
                    }
                ]
            }
        }
    }
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore aggiornamento record {page_id}: {e}")
        return False

def update_data_json():
    """Aggiorna il file data.json con le descrizioni censurate"""
    print("📝 Aggiornando file data.json...")
    
    try:
        # Leggi il file data.json esistente
        with open("public/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Controlla la struttura dei dati
        if isinstance(data, dict) and "results" in data:
            records = data["results"]
        elif isinstance(data, list):
            records = data
        else:
            print("❌ Struttura data.json non riconosciuta")
            return False
        
        updated_count = 0
        total_censored = 0
        
        for record in records:
            # Censura Descrizione_originale se presente
            if "Descrizione_originale" in record and record["Descrizione_originale"]:
                original = record["Descrizione_originale"]
                censored = censor_sensitive_data(original)
                
                if censored != original:
                    record["Descrizione_originale"] = censored
                    updated_count += 1
                    stats = get_censorship_stats(original)
                    total_censored += sum(stats.values())
                    print(f"🔒 Censurato record: {record.get('title', 'Senza titolo')[:50]}...")
            
            # Censura anche description se presente
            if "description" in record and record["description"]:
                original = record["description"]
                censored = censor_sensitive_data(original)
                
                if censored != original:
                    record["description"] = censored
                    updated_count += 1
                    stats = get_censorship_stats(original)
                    total_censored += sum(stats.values())
                    print(f"🔒 Censurato description: {record.get('title', 'Senza titolo')[:50]}...")
        
        # Salva il file aggiornato
        with open("public/data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Aggiornati {updated_count} record in data.json")
        print(f"📊 Totale elementi censurati: {total_censored}")
        return True
        
    except Exception as e:
        print(f"❌ Errore aggiornamento data.json: {e}")
        return False

def main():
    """Funzione principale"""
    print("🔒 SCRIPT DI CENSURA DATABASE NOTION")
    print("=" * 60)
    print(f"⏰ Avviato il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Recupera tutti i record da Notion
    records = get_all_notion_records()
    
    if not records:
        print("❌ Nessun record trovato nel database")
        return
    
    # 2. Processa e aggiorna i record
    print("\n🔄 Processando record Notion...")
    updated_count = 0
    total_censored = 0
    
    for record in records:
        page_id = record["id"]
        properties = record.get("properties", {})
        
        # Estrai Descrizione_originale
        desc_prop = properties.get("Descrizione_originale", {})
        if desc_prop and "rich_text" in desc_prop:
            rich_text = desc_prop["rich_text"]
            if rich_text:
                original_description = rich_text[0]["text"]["content"]
                
                # Censura la descrizione
                censored_description = censor_sensitive_data(original_description)
                
                # Aggiorna solo se è cambiata
                if censored_description != original_description:
                    if update_notion_record(page_id, censored_description):
                        updated_count += 1
                        stats = get_censorship_stats(original_description)
                        total_censored += sum(stats.values())
                        
                        title = properties.get("Titolo_parafrasato", {}).get("title", [{}])[0].get("text", {}).get("content", "Senza titolo")
                        print(f"🔒 Censurato: {title[:50]}...")
    
    print(f"\n✅ Aggiornati {updated_count} record in Notion")
    print(f"📊 Totale elementi censurati: {total_censored}")
    
    # 3. Aggiorna data.json
    print("\n📝 Aggiornando data.json...")
    if update_data_json():
        print("✅ data.json aggiornato con successo")
    else:
        print("❌ Errore nell'aggiornamento di data.json")
    
    # 4. Statistiche finali
    print("\n📊 STATISTICHE FINALI")
    print("=" * 60)
    print(f"📄 Record processati: {len(records)}")
    print(f"🔒 Record aggiornati: {updated_count}")
    print(f"📊 Elementi censurati: {total_censored}")
    print(f"⏰ Completato il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 5. Auto-cancellazione
    print("\n🗑️ Auto-cancellazione script...")
    try:
        os.remove(__file__)
        print("✅ Script auto-cancellato con successo")
    except Exception as e:
        print(f"⚠️ Errore auto-cancellazione: {e}")
        print("   Cancella manualmente il file censor_notion_database.py")

if __name__ == "__main__":
    main()
