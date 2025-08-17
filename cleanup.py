import os
import requests
import json
import time
from datetime import datetime, timedelta

# CONFIGURAZIONE
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

# Cambia questo per testare senza cancellare
MODALITA_TEST = True  # ⚠️ Metti False per cancellare davvero

HEADERS_NOTION = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Headers per simulare un browser reale più moderno
FACEBOOK_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'DNT': '1',
    'Referer': 'https://www.google.com/',
}

def get_all_notion_entries():
    """Recupera tutti gli entry dal database Notion con i loro page_id."""
    print("🔍 Recupero tutti gli annunci dal database Notion...")
    
    all_entries = []
    has_more = True
    next_cursor = None
    
    while has_more:
        query_payload = {
            "page_size": 100
        }
        
        if next_cursor:
            query_payload["start_cursor"] = next_cursor
            
        try:
            response = requests.post(
                f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query",
                headers=HEADERS_NOTION,
                json=query_payload
            )
            
            if response.status_code != 200:
                print(f"❌ ERRORE: Non riesco a leggere il database Notion: {response.text}")
                break
                
            data = response.json()
            
            for page in data.get("results", []):
                page_id = page["id"]
                properties = page.get("properties", {})
                
                # Estrai il link
                link_prop = properties.get("Link", {})
                link = link_prop.get("url", "")
                
                # Estrai il titolo per il log
                title_prop = properties.get("Titolo_parafrasato", {})
                title = ""
                if title_prop.get("title"):
                    title = title_prop["title"][0]["text"]["content"] if title_prop["title"] else ""
                
                if link:  # Solo se ha un link
                    all_entries.append({
                        "page_id": page_id,
                        "link": link,
                        "title": title
                    })
            
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
            
        except Exception as e:
            print(f"❌ ERRORE: Problema durante il recupero degli annunci: {e}")
            break
    
    print(f"📋 TROVATI {len(all_entries)} annunci con link Facebook nel database")
    return all_entries

def is_facebook_link_active(url, timeout=15):
    """
    Controlla se un link Facebook è ancora attivo.
    Restituisce True se attivo, False se non attivo/eliminato.
    """
    try:
        # Aggiungi un session object per persistere i cookies
        session = requests.Session()
        session.headers.update(FACEBOOK_HEADERS)
        
        # Metodo 1: HEAD request (più veloce, meno dati)
        head_response = session.head(
            url, 
            timeout=timeout,
            allow_redirects=True
        )
        
        print(f"   📊 Status code ricevuto: {head_response.status_code}")
        
        # Codici di stato che indicano chiaramente contenuto non disponibile
        if head_response.status_code in [404, 403, 410, 451]:
            print(f"   🔴 Status code {head_response.status_code} - Link sicuramente inattivo")
            return False
        
        # Facebook restituisce 400 per bot detection - proviamo con GET
        if head_response.status_code == 400:
            print(f"   🟡 Status 400 (possibile bot detection), provo con GET limitata...")
            return _check_with_limited_get_session(session, url, timeout)
        
        # Se HEAD restituisce 200, probabilmente è attivo
        if head_response.status_code == 200:
            # Verifica aggiuntiva: controlla header specifici di Facebook
            content_type = head_response.headers.get('content-type', '').lower()
            
            # Se non è HTML, probabilmente è un redirect o errore
            if 'text/html' not in content_type:
                print(f"   🟡 Content-type sospetto: {content_type} - Probabilmente inattivo")
                return False
            
            # Controlla se c'è un redirect verso pagina di errore Facebook
            final_url = head_response.url
            error_patterns = [
                'facebook.com/unsupportedbrowser',
                'facebook.com/login',
                'facebook.com/checkpoint',
                'm.facebook.com/login',
                'facebook.com/sorry',
                'facebook.com/error'
            ]
            
            for pattern in error_patterns:
                if pattern in final_url.lower():
                    print(f"   🔴 Redirect verso pagina di errore Facebook - Link inattivo")
                    return False
            
            print(f"   🟢 Status 200 + HTML valido - Link attivo")
            return True
        
        # Per altri status code, facciamo una GET limitata
        if head_response.status_code in [405, 501]:
            print(f"   🟡 HEAD non supportato (status {head_response.status_code}), provo con GET...")
            return _check_with_limited_get_session(session, url, timeout)
        
        # Status code ambigui (500, 503, ecc.) - consideriamo temporaneamente attivo
        if head_response.status_code >= 500:
            print(f"   🟡 Errore server temporaneo (status {head_response.status_code}) - Considero attivo per ora")
            return True
        
        # Altri status code - probabilmente inattivo
        print(f"   🔴 Status code {head_response.status_code} - Considero inattivo")
        return False
        
    except requests.exceptions.Timeout:
        print(f"   ⏱️ Timeout dopo {timeout}s - Il link potrebbe essere lento ma attivo")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️ Errore di rete: {e} - Considero attivo per sicurezza")
        return True

def _check_with_limited_get_session(session, url, timeout=15):
    """Fallback: fa una GET ma scarica solo i primi KB per verificare il contenuto."""
    try:
        # Aggiungi un delay casuale per sembrare più umano
        import random
        time.sleep(random.uniform(1, 3))
        
        response = session.get(
            url, 
            timeout=timeout,
            allow_redirects=True,
            stream=True
        )
        
        print(f"   📊 GET Status code: {response.status_code}")
        
        if response.status_code == 404:
            print(f"   🔴 GET restituisce 404 - Link definitivamente inattivo")
            return False
        
        if response.status_code == 400:
            print(f"   🔴 GET restituisce 400 - Facebook blocca le richieste automatiche")
            print(f"   💡 Suggerimento: Questo link potrebbe essere attivo, ma non verificabile automaticamente")
            # In caso di 400, consideriamo il link attivo per evitare false eliminazioni
            return True
        
        # Leggi solo i primi 3KB della risposta
        content_chunk = ""
        chunk_size = 0
        max_chunk_size = 3072  # 3KB
        
        try:
            for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
                if chunk:
                    content_chunk += chunk
                    chunk_size += len(chunk)
                    if chunk_size >= max_chunk_size:
                        break
        except UnicodeDecodeError:
            # Se c'è un errore di encoding, probabilmente è una pagina valida
            print(f"   🟡 Errore decodifica - probabilmente pagina valida")
            response.close()
            return True
        
        response.close()
        
        # Verifica rapida su questo piccolo chunk
        content_lower = content_chunk.lower()
        
        # Pattern che indicano chiaramente pagina di errore (nei primi 3KB)
        error_patterns = [
            '<title>content not available',
            '<title>contenuto non disponibile',
            'questo contenuto non è al momento disponibile',
            'this content isn\'t available right now',
            'content unavailable',
            'post not found',
            'pagina non trovata',
            'sorry, something went wrong',
            'page not found',
            'content isn\'t available'
        ]
        
        for pattern in error_patterns:
            if pattern in content_lower:
                print(f"   🔴 Trovato messaggio di errore nella pagina - Link inattivo")
                return False
        
        # Controlla se è una pagina di login/errore di Facebook
        facebook_error_patterns = [
            'facebook.com/login',
            'log in to facebook',
            'accedi a facebook',
            'create account',
            'crea account'
        ]
        
        for pattern in facebook_error_patterns:
            if pattern in content_lower:
                print(f"   🔴 Redirect verso login Facebook - Link probabilmente inattivo")
                return False
        
        print(f"   🟢 Nessun messaggio di errore trovato - Link sembra attivo")
        return True
        
    except Exception as e:
        print(f"   ⚠️ Errore GET limitata: {e} - Considero attivo per sicurezza")
        return True

def delete_notion_page(page_id):
    """Elimina una pagina dal database Notion archiviandola."""
    try:
        response = requests.patch(
            f"https://api.notion.com/v1/pages/{page_id}",
            headers=HEADERS_NOTION,
            json={"archived": True}
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"      ❌ ERRORE eliminazione: {response.text}")
            return False
            
    except Exception as e:
        print(f"      ❌ ERRORE durante eliminazione: {e}")
        return False

def main():
    """Funzione principale per il cleanup"""
    print("=" * 60)
    if MODALITA_TEST:
        print("🧪 MODALITÀ TEST - NESSUN ANNUNCIO VERRÀ CANCELLATO")
    else:
        print("🗑️ MODALITÀ ELIMINAZIONE - GLI ANNUNCI INATTIVI VERRANNO CANCELLATI")
    print("=" * 60)
    
    entries = get_all_notion_entries()
    
    if not entries:
        print("ℹ️ Nessun annuncio con link trovato nel database. Fine.")
        return
    
    print(f"\n🔍 Inizio controllo di {len(entries)} link...")
    print("-" * 60)
    
    inactive_links = []
    active_count = 0
    
    for i, entry in enumerate(entries):
        print(f"\n[{i+1}/{len(entries)}] 🔍 CONTROLLO: {entry['title'][:60]}...")
        print(f"   Link: {entry['link']}")
        
        is_active = is_facebook_link_active(entry["link"])
        
        if not is_active:
            inactive_links.append(entry)
            print(f"   ❌ RISULTATO: LINK INATTIVO - Verrà {'eliminato' if not MODALITA_TEST else 'marcato per eliminazione'}")
        else:
            active_count += 1
            print(f"   ✅ RISULTATO: LINK ATTIVO - Mantieni")
        
        # Pausa per non sovraccaricare Facebook (aumentata)
        if i < len(entries) - 1:
            delay = 5 + (i % 3)  # Delay variabile tra 5-7 secondi
            print(f"   ⏳ Pausa {delay} secondi per evitare rate limiting...")
            time.sleep(delay)
    
    print("\n" + "=" * 60)
    print("📊 RIEPILOGO FINALE:")
    print(f"   📋 Annunci totali controllati: {len(entries)}")
    print(f"   ✅ Link ancora attivi: {active_count}")
    print(f"   ❌ Link inattivi trovati: {len(inactive_links)}")
    print("=" * 60)
    
    if inactive_links:
        print(f"\n🗑️ ELENCO ANNUNCI CON LINK INATTIVI:")
        print("-" * 60)
        for i, entry in enumerate(inactive_links):
            print(f"{i+1}. {entry['title']}")
            print(f"   Link: {entry['link']}")
        print("-" * 60)
        
        if MODALITA_TEST:
            print(f"🧪 MODALITÀ TEST: I {len(inactive_links)} annunci sopra VERREBBERO eliminati")
            print("💡 Per eliminarli davvero, cambia MODALITA_TEST = False nel codice")
        else:
            print(f"🗑️ ELIMINO {len(inactive_links)} annunci inattivi dal database...")
            deleted_count = 0
            
            for i, entry in enumerate(inactive_links):
                print(f"\n[{i+1}/{len(inactive_links)}] 🗑️ Elimino: {entry['title'][:50]}...")
                
                if delete_notion_page(entry["page_id"]):
                    deleted_count += 1
                    print(f"      ✅ ELIMINATO con successo")
                else:
                    print(f"      ❌ ERRORE durante eliminazione")
                
                # Pausa tra le eliminazioni
                if i < len(inactive_links) - 1:
                    time.sleep(2)
            
            print(f"\n🎉 CLEANUP COMPLETATO!")
            print(f"   ✅ Eliminati con successo: {deleted_count}/{len(inactive_links)}")
            if deleted_count < len(inactive_links):
                print(f"   ⚠️ Errori durante eliminazione: {len(inactive_links) - deleted_count}")
    else:
        print(f"\n🎉 OTTIMO! Tutti i link sono ancora attivi.")
        print("   Nessun annuncio da eliminare.")

if __name__ == "__main__":
    main()
