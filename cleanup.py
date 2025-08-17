# Aggiungi la libreria per pattern URL
import re
from urllib.parse import urlparse, parse_qs

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

# APPROCCI ALTERNATIVI PER CONTROLLARE LINK FACEBOOK
# 1. Servizi di terze parti
# 2. Controllo pattern URL
# 3. Controllo metadata

import re
from urllib.parse import urlparse, parse_qs

def is_facebook_link_active(url, timeout=15):
    """
    Controlla se un link Facebook è ancora attivo usando approcci alternativi.
    Restituisce True se attivo, False se non attivo/eliminato.
    """
    
    # APPROCCIO 1: Analisi pattern URL
    url_validity = _analyze_facebook_url_pattern(url)
    if url_validity == "invalid":
        print(f"   🔴 Pattern URL non valido - Link sicuramente inattivo")
        return False
    elif url_validity == "suspicious":
        print(f"   🟡 Pattern URL sospetto - Potrebbe essere inattivo")
    
    # APPROCCIO 2: Controllo con servizi esterni
    external_check = _check_with_external_service(url)
    if external_check is not None:
        return external_check
    
    # APPROCCIO 3: Controllo leggero con requests (fallback)
    return _lightweight_facebook_check(url, timeout)

def _analyze_facebook_url_pattern(url):
    """Analizza pattern URL Facebook per identificare link probabilmente inattivi"""
    try:
        parsed = urlparse(url)
        
        # Controlla se è davvero Facebook
        if 'facebook.com' not in parsed.netloc.lower():
            return "invalid"
        
        path = parsed.path.lower()
        
        # Pattern di URL che indicano post/gruppi validi
        valid_patterns = [
            r'/groups/\d+/posts/\d+',      # Post nei gruppi
            r'/groups/[^/]+/posts/\d+',    # Post nei gruppi con nome
            r'/\w+/posts/\d+',             # Post nelle pagine
            r'/photo\.php\?',               # Foto
            r'/events/\d+',                 # Eventi
            r'/marketplace/item/\d+',       # Marketplace
        ]
        
        # Pattern sospetti o non validi
        invalid_patterns = [
            r'/login',
            r'/checkpoint',
            r'/error',
            r'/sorry',
            r'/unsupportedbrowser',
            r'/help/',
        ]
        
        # Controlla pattern non validi
        for pattern in invalid_patterns:
            if re.search(pattern, path):
                return "invalid"
        
        # Controlla pattern validi
        has_valid_pattern = any(re.search(pattern, path) for pattern in valid_patterns)
        
        # Controlla se l'ID del post sembra troppo vecchio o malformato
        post_id_match = re.search(r'/posts/(\d+)', path)
        if post_id_match:
            post_id = post_id_match.group(1)
            # ID molto corti o molto lunghi sono sospetti
            if len(post_id) < 10 or len(post_id) > 20:
                print(f"   🟡 ID post sospetto: {post_id} (lunghezza: {len(post_id)})")
                return "suspicious"
        
        return "valid" if has_valid_pattern else "unknown"
        
    except Exception as e:
        print(f"   ⚠️ Errore analisi URL pattern: {e}")
        return "unknown"

def _check_with_external_service(url):
    """Usa servizi esterni per verificare la validità del link"""
    try:
        # SERVIZIO 1: URLVoid API (gratis con limiti)
        # Nota: Questo è solo un esempio, dovrai registrarti per ottenere una API key
        
        # SERVIZIO 2: Link checker generico
        checker_url = "https://httpstatus.io/"
        
        # Per ora, saltiamo i servizi esterni per evitare dipendenze
        # In futuro potresti integrare servizi come:
        # - URLVoid
        # - Pingdom
        # - GTmetrix
        # - WebPageTest
        
        return None  # Nessun controllo esterno per ora
        
    except Exception as e:
        print(f"   ⚠️ Errore servizio esterno: {e}")
        return None

def _lightweight_facebook_check(url, timeout=10):
    """
    Controllo molto leggero che cerca di minimizzare la detection di Facebook.
    Usa tecniche meno aggressive.
    """
    try:
        print(f"   🔍 Tentativo controllo leggero...")
        
        # Headers minimalisti - sembrano meno un bot
        minimal_headers = {
            'User-Agent': 'curl/7.68.0',  # Spesso curl è meno bloccato
            'Accept': '*/*',
        }
        
        # Prima prova: solo HEAD con timeout molto basso
        response = requests.head(
            url,
            headers=minimal_headers,
            timeout=5,  # Timeout basso
            allow_redirects=False  # Non seguire redirect
        )
        
        print(f"   📊 Status HEAD (senza redirect): {response.status_code}")
        
        # Analizza solo il primo status code
        if response.status_code == 200:
            print(f"   🟢 Status 200 diretto - Link probabilmente attivo")
            return True
        elif response.status_code in [301, 302, 303, 307, 308]:
            # È un redirect, segui UNA volta
            location = response.headers.get('location', '')
            if location:
                print(f"   🔄 Redirect verso: {location[:100]}...")
                
                # Controlla se il redirect va verso pagine di errore
                error_indicators = [
                    'login', 'checkpoint', 'error', 'sorry', 
                    'unsupportedbrowser', 'help'
                ]
                
                if any(indicator in location.lower() for indicator in error_indicators):
                    print(f"   🔴 Redirect verso pagina di errore - Link inattivo")
                    return False
                else:
                    print(f"   🟡 Redirect normale - Link probabilmente attivo")
                    return True
        elif response.status_code == 404:
            print(f"   🔴 Status 404 - Link definitivamente inattivo")
            return False
        elif response.status_code == 403:
            print(f"   🔴 Status 403 - Accesso negato, link probabilmente inattivo")
            return False
        else:
            print(f"   🟡 Status {response.status_code} - Stato ambiguo, considero attivo")
            return True
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️ Timeout rapido - Il server risponde lentamente, considero attivo")
        return True
    except requests.exceptions.ConnectionError:
        print(f"   🔴 Errore connessione - Possibile link inattivo")
        return False
    except Exception as e:
        print(f"   ⚠️ Errore generico: {e} - Considero attivo per sicurezza")
        return True

# Rimuovi le vecchie funzioni non più usate

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
