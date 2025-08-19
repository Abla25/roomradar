import os
import requests
import json
import time
import feedparser
import re
import unicodedata
from datetime import datetime, timedelta
from rapidfuzz import fuzz
from zone_mapping import BARCELONA_MACRO_ZONES, MACRO_ZONE_MAPPING
from bs4 import BeautifulSoup
from censorship import censor_sensitive_data, has_sensitive_data

# CONFIGURAZIONE
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL_NAME = "meta-llama/llama-3.3-70b-instruct:free"

# Cache per URL scartati dall'AI
CACHE_FILE = "rejected_urls_cache.json"
CACHE_CLEANUP_HOURS = 48
MAX_CACHE_SIZE = 1000  # Massimo numero di URL in cache

# Cache in memoria per performance
_cache_data = None
_cache_last_load = None

# Cache per calcoli di similarità (evita ricalcoli)
_similarity_cache = {}

# Cache per normalizzazione testo
_text_normalization_cache = {}



def load_rejected_cache():
    """Carica la cache degli URL scartati dall'AI con TTL individuale."""
    global _cache_data, _cache_last_load
    
    # Controlla se il file è stato modificato
    if os.path.exists(CACHE_FILE):
        file_mtime = os.path.getmtime(CACHE_FILE)
        if _cache_data is not None and _cache_last_load == file_mtime:
            return _cache_data  # Usa cache in memoria
    
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Pulisci URL scaduti (TTL individuale)
                current_time = datetime.now()
                expired_urls = []
                cleaned_urls = {}
                
                for url, url_data in data.get('urls', {}).items():
                    url_timestamp = datetime.fromisoformat(url_data['timestamp'])
                    if current_time - url_timestamp > timedelta(hours=CACHE_CLEANUP_HOURS):
                        expired_urls.append(url)
                    else:
                        cleaned_urls[url] = url_data
                
                if expired_urls:
                    print(f"🗑️ Removed {len(expired_urls)} expired URLs from cache (TTL {CACHE_CLEANUP_HOURS}h)")
                
                _cache_data = {
                    'urls': cleaned_urls,
                    'timestamp': current_time.isoformat()
                }
                _cache_last_load = file_mtime
                return _cache_data
        except Exception as e:
            print(f"⚠️ Cache loading error: {e}")
    
    _cache_data = {'urls': {}, 'timestamp': datetime.now().isoformat()}
    _cache_last_load = None
    return _cache_data

def save_rejected_cache(cache_data):
    """Salva la cache degli URL scartati dall'AI."""
    global _cache_data, _cache_last_load
    
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        # Aggiorna cache in memoria
        _cache_data = cache_data
        _cache_last_load = os.path.getmtime(CACHE_FILE) if os.path.exists(CACHE_FILE) else None
        
        print(f"💾 Cache saved to: {os.path.abspath(CACHE_FILE)}")
        print(f"📊 URLs in cache: {len(cache_data['urls'])}")
    except Exception as e:
        print(f"⚠️ Cache save error: {e}")

def add_to_rejected_cache(url, reason="AI_SCRUTINY"):
    """Aggiunge un URL alla cache degli scartati con logica FIFO."""
    print(f"🔄 Adding URL to cache: {url} (reason: {reason})")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"📁 Cache file: {os.path.abspath(CACHE_FILE)}")
    
    cache_data = load_rejected_cache()
    
    # Se la cache è piena, rimuovi gli URL più vecchi (FIFO)
    if len(cache_data['urls']) >= MAX_CACHE_SIZE:
        print(f"🗑️ Cache full ({MAX_CACHE_SIZE} URLs), removing oldest URLs (FIFO)...")
        # Ordina per timestamp (più vecchi prima) e rimuovi il 50% più vecchio
        sorted_urls = sorted(cache_data['urls'].items(), 
                           key=lambda x: x[1]['timestamp'])
        # Rimuovi il 50% più vecchio per fare spazio (corretto)
        remove_count = int(MAX_CACHE_SIZE * 0.5)  # 50% del limite
        cache_data['urls'] = dict(sorted_urls[remove_count:])
        print(f"🗑️ Removed {remove_count} oldest URLs (FIFO - 50%)")
    
    cache_data['urls'][url] = {
        'reason': reason,
        'timestamp': datetime.now().isoformat()
    }
    save_rejected_cache(cache_data)
    
    # Verifica immediata che il file sia stato creato
    if os.path.exists(CACHE_FILE):
        file_size = os.path.getsize(CACHE_FILE)
        print(f"✅ Verification: Cache file created successfully ({file_size} bytes)")
    else:
        print(f"❌ ERROR: Cache file NOT found after saving!")

def is_url_rejected(url):
    """Controlla se un URL è nella cache degli scartati."""
    cache_data = load_rejected_cache()
    return url in cache_data['urls']

def get_cache_stats():
    """Restituisce statistiche dettagliate sulla cache."""
    cache_data = load_rejected_cache()
    urls = cache_data['urls']
    
    if not urls:
        return 0, 0, 0
    
    # Calcola età media degli URL in cache
    current_time = datetime.now()
    ages = []
    for url_data in urls.values():
        url_time = datetime.fromisoformat(url_data['timestamp'])
        age_hours = (current_time - url_time).total_seconds() / 3600
        ages.append(age_hours)
    
    avg_age = sum(ages) / len(ages)
    oldest_age = max(ages)
    
    return len(urls), avg_age, oldest_age

# Configurazione RSS URLs - Supporto per multiple feed
RSS_URLS = []

# Debug iniziale per configurazione RSS

# Cerca RSS_URL_1, RSS_URL_2, RSS_URL_3, etc.
i = 1
while f"RSS_URL_{i}" in os.environ:
    url = os.environ[f"RSS_URL_{i}"]
    if url and url.strip():  # Verifica che l'URL non sia vuoto
        RSS_URLS.append(url.strip())
        print(f"✅ Added RSS_URL_{i}: {url.strip()}")
    else:
        print(f"⚠️ RSS_URL_{i} is empty or contains only spaces")
    i += 1

# Fallback per compatibilità con il formato legacy (singolo URL)
if not RSS_URLS and "RSS_URL" in os.environ:
    url = os.environ["RSS_URL"]
    if url and url.strip():
        RSS_URLS.append(url.strip())
        print(f"✅ Added RSS_URL: {url.strip()}")
    else:
        print(f"⚠️ RSS_URL is empty or contains only spaces")

if not RSS_URLS:
    print("❌ Nessun RSS URL valido trovato nei secrets")
    print("🔍 Debug: Tutte le variabili d'ambiente che iniziano con RSS_URL:")
    for key, value in os.environ.items():
        if key.startswith("RSS_URL"):
            print(f"  {key}: '{value}'")
    raise ValueError("❌ Nessun RSS URL configurato. Definisci RSS_URL_1, RSS_URL_2, RSS_URL_3, etc. o RSS_URL (singolo).")

    print(f"📡 Configured {len(RSS_URLS)} RSS feeds:")
for i, url in enumerate(RSS_URLS, 1):
    print(f"  {i}. {url}")

MAX_BATCH = 3
MIN_BATCH = 1
INITIAL_BACKOFF_SECONDS = 32
MAX_BACKOFF_SECONDS = 62

# Soglie similarità per deduplica
HIGH_DUP_THRESHOLD = 0.85  # sopra questa soglia segniamo direttamente il vecchio come "expired"

HEADERS_NOTION = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

PROMPT_TEMPLATE = """
Analyze the following posts and return valid JSON for each one.
Exclude all posts where someone is LOOKING for a room or apartment,
or posts that don't concern real rentals, or posts related to short-term vacation rentals with daily prices. The only relevant posts are those related to room/accommodation listings that are being rented out.

IMPORTANT: 
- For all fields, if the information is not available or cannot be extracted from the post, always use "N/A" as the value. Don't leave fields empty and don't use "Not specified" or similar.
- ALL OUTPUT MUST BE IN ENGLISH ONLY. Do not respond in Spanish, Italian, or any other language.

For each relevant post, generate a dictionary with:
{{
  "relevant_listing": "YES" or "NO",
  "paraphrased_title": "..." (in English),
  "overview": "..." (in English),
  "price": "..." (use "N/A" if not available),
  "zone": "..." (use "N/A" if not available),
  "rooms": "..." (use "N/A" if not available),
  "reliability": number (0-5) (based on information completeness, photos presence, contacts availability, and absence of scam indicators; 4 and 5 can only be achieved if photos are present and it doesn't seem like a scam),
  "rating_reason": "..." (EXPLAIN IN ENGLISH why you gave this reliability score),
}}
Respond ONLY with JSON. No additional text. All text fields must be in English.
POSTS:
{posts}
"""

def _extract_text_property(prop: dict) -> str:
    """Estrae plain text da una property Notion di tipo title/rich_text."""
    if not isinstance(prop, dict):
        return ""
    if "title" in prop:
        return " ".join([t.get("plain_text", "") for t in prop.get("title", [])]).strip()
    if "rich_text" in prop:
        return " ".join([t.get("plain_text", "") for t in prop.get("rich_text", [])]).strip()
    return ""

def _extract_status_name(prop: dict) -> str:
    if not isinstance(prop, dict):
        return ""
    # Supporta sia proprietà di tipo "status" sia "select"
    if isinstance(prop.get("status"), dict):
        return prop.get("status", {}).get("name", "") or ""
    if isinstance(prop.get("select"), dict):
        return prop.get("select", {}).get("name", "") or ""
    return ""

def normalize_text(text: str) -> str:
    """Normalizza il testo con cache per evitare ricalcoli."""
    if text in _text_normalization_cache:
        return _text_normalization_cache[text]
    
    normalized = (text or "").lower()
    normalized = re.sub(r"https?://\S+", " ", normalized)
    normalized = re.sub(r"[\W_]+", " ", normalized, flags=re.UNICODE)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    
    # Cache per testi fino a 1000 caratteri (evita memory leak)
    if len(text) <= 1000:
        _text_normalization_cache[text] = normalized
    
    return normalized

def _normalize_for_zone(text: str) -> str:
    if not text:
        return ""
    # Rimuove accenti, minuscole, normalizza spazi e apostrofi
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = text.replace("'", " ")
    text = re.sub(r"[\W_]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def infer_macro_zone(zona: str, titolo: str = "", descrizione: str = "") -> tuple[str, str]:
    """Mappa una zona/quartiere di Barcellona in una macro-zona predefinita.
    Ritorna (macro_zone, zona_matched) se determinabile, altrimenti ("", "").
    Se non determinabile, restituisce stringa vuota.
    Peso maggiore al match su 'zona', poi su titolo/descrizione.
    """
    zona_norm = _normalize_for_zone(zona)
    titolo_norm = _normalize_for_zone(titolo)
    descr_norm = _normalize_for_zone(descrizione)
    corpus_norm = f"{titolo_norm} {descr_norm}".strip()

    best_macro = ""
    best_score = 0
    best_token = ""
    for macro, tokens in MACRO_ZONE_MAPPING.items():
        score = 0
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            if zona_norm and token in zona_norm:
                score += 2
                if score > best_score:
                    best_score = score
                    best_macro = macro
                    best_token = token
            elif token in corpus_norm:
                score += 1
                if score > best_score:
                    best_score = score
                    best_macro = macro
                    best_token = token
        if score > best_score:
            best_score = score
            best_macro = macro

    return (best_macro, best_token) if best_score > 0 else ("", "")

def similarity_score(a: str, b: str) -> float:
    """Calcola similarità con cache per evitare ricalcoli."""
    # Crea una chiave unica per la coppia (ordinata per simmetria)
    key = tuple(sorted([a, b]))
    if key in _similarity_cache:
        return _similarity_cache[key]
    
    a_norm, b_norm = normalize_text(a), normalize_text(b)
    if not a_norm or not b_norm:
        _similarity_cache[key] = 0.0
        return 0.0
    
    # Evita confronti con testi troppo corti (meno di 10 caratteri)
    if len(a_norm) < 10 or len(b_norm) < 10:
        _similarity_cache[key] = 0.0
        return 0.0
    
    # Calcola similarità usando token_set_ratio per maggiore accuratezza
    score = fuzz.token_set_ratio(a_norm, b_norm) / 100.0
    
    # Bonus per testi molto simili in lunghezza
    length_diff = abs(len(a_norm) - len(b_norm)) / max(len(a_norm), len(b_norm))
    if length_diff < 0.1:  # Se la differenza di lunghezza è < 10%
        score = min(score + 0.05, 1.0)  # Bonus del 5%
    
    _similarity_cache[key] = score
    return score

def safe_number(value):
    if value is None:
        return None
    try:
        text = str(value).strip()
        if text == "":
            return None
        return float(text)
    except Exception:
        return None

def get_existing_data():
    """Recupera tutti i dati esistenti dal database Notion in una sola chiamata ottimizzata."""
    existing_links = set()
    existing_pages = []
    has_more = True
    next_cursor = None
    
    print("📋 Caricamento dati esistenti dal database...")
    
    while has_more:
        query_payload = {
            "page_size": 100,
            "sorts": [
                {
                    "property": "date_added",
                    "direction": "descending"
                }
            ]
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
                print(f"❌ Error retrieving existing data: {response.text}")
                break
                
            data = response.json()
            
            for page in data.get("results", []):
                props = page.get("properties", {})
                
                # Estrai link
                link_prop = props.get("Link", {})
                link_url = link_prop.get("url", "")
                if link_url:
                    existing_links.add(link_url)
                
                # Estrai dati per deduplicazione
                existing_pages.append({
                    "id": page.get("id"),
                    "created_time": page.get("created_time"),
                            "paraphrased_title": _extract_text_property(props.get("paraphrased_title", {})),
        "original_description": _extract_text_property(props.get("original_description", {})),
        "price": _extract_text_property(props.get("price", {})),
                    "zone": _extract_text_property(props.get("zone", {})),
                    "status": _extract_status_name(props.get("status", {})),
                    "Link": link_url
                })
            
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
            
        except Exception as e:
            print(f"❌ Error during data retrieval: {e}")
            break
    
    print(f"📋 Found {len(existing_links)} links and {len(existing_pages)} existing pages")
    return existing_links, existing_pages

def find_best_duplicate_optimized(existing_pages: list, new_descr: str, threshold: float = 0.8):
    """Versione ottimizzata che ferma la ricerca quando trova un match sopra la soglia."""
    best_page = None
    best_score = 0.0
    
    # Pre-normalizza la nuova descrizione una sola volta
    new_descr_norm = normalize_text(new_descr)
    
    # Ordina le pagine per data di creazione (più recenti prima) per trovare duplicati più velocemente
    sorted_pages = sorted(existing_pages, key=lambda x: x.get("created_time", ""), reverse=True)
    
    for p in sorted_pages:
        descr = p.get("original_description", "")
        if not descr:
            continue
            
        # Normalizza anche la descrizione esistente per confronto accurato
        descr_norm = normalize_text(descr)
        
        # Calcola similarità usando testi normalizzati per maggiore accuratezza
        score = similarity_score(new_descr_norm, descr_norm)
        
        if score > best_score:
            best_score = score
            best_page = p
            
            # Early exit: se abbiamo trovato un match molto forte, fermiamoci
            if score >= threshold:
                break
    
    return best_page, best_score

def extract_images_from_description(description):
    """Estrae gli URL delle immagini dal contenuto HTML della descrizione"""
    if not description:
        return []
    
    # Pattern per trovare tutti i tag img
    img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
    matches = re.findall(img_pattern, description, re.IGNORECASE)
    
    # Decodifica le entità HTML negli URL (es. &amp; -> &)
    import html
    decoded_matches = []
    for url in matches:
        decoded_url = html.unescape(url)
        decoded_matches.append(decoded_url)
    
    return decoded_matches

def extract_images_from_media_content(entry):
    """Estrae gli URL delle immagini dal tag media:content"""
    images = []
    
    if hasattr(entry, 'media_content'):
        for media in entry.media_content:
            if hasattr(media, 'medium') and media.medium == 'image':
                if hasattr(media, 'url'):
                    images.append(media.url)
    
    return images

def clean_html_from_description(description):
    """Rimuove HTML e immagini dalla descrizione, mantenendo solo il testo puro"""
    if not description:
        return ""
    
    # Usa BeautifulSoup per rimuovere tutti i tag HTML
    soup = BeautifulSoup(description, 'html.parser')
    
    # Rimuovi tutti i tag img
    for img in soup.find_all('img'):
        img.decompose()
    
    # Estrai solo il testo
    clean_text = soup.get_text(separator=' ', strip=True)
    
    # Pulisci spazi multipli
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text

def extract_all_images(entry):
    """Estrae tutte le immagini da un entry RSS, rimuovendo duplicati"""
    desc_images = extract_images_from_description(entry.description)
    media_images = extract_images_from_media_content(entry)
    
    # Combina e rimuovi duplicati
    all_images = list(set(desc_images + media_images))
    return all_images

def clear_caches():
    """Pulisce le cache in memoria per evitare memory leak."""
    global _similarity_cache, _text_normalization_cache
    
    # Mantieni solo le ultime 1000 entry per evitare memory leak
    if len(_similarity_cache) > 1000:
        _similarity_cache.clear()
    if len(_text_normalization_cache) > 1000:
        _text_normalization_cache.clear()



def mark_status_expired(page_id: str):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": {"status": {"select": {"name": "expired"}}}}
    res = requests.patch(url, headers=HEADERS_NOTION, json=payload)
    if res.status_code != 200:
        print(f"❌ Error updating status=expired for {page_id}: {res.text}")
    else:
        print(f"🗂️ Set status=expired for page {page_id}")





def parse_llm_json(raw_text, retries=3):
    """Tenta di parsare JSON da testo grezzo con retry."""
    for attempt in range(retries):
        raw_text = raw_text.strip()
        if not raw_text:
            print(f"⚠️ Empty response. Retry {attempt+1}/{retries}")
            time.sleep(2 ** attempt)
            continue
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON. Retry {attempt+1}/{retries}")
            time.sleep(2 ** attempt)
    return None

def ai_macro_zone_from_zone(zona_text: str) -> str:
    """Chiede al modello di mappare una zona/quartiere alla macro-zona predefinita.
    Ritorna stringa vuota se non determinabile o risposta non valida.
    """
    if not zona_text:
        return ""
    macro_list = "\n- " + "\n- ".join(BARCELONA_MACRO_ZONES)
    prompt = f"""
Ti fornisco una zona/quartiere di Barcellona. Scegli quale macro-zona corrisponde, SOLO tra questa lista. Se non sei sicuro, restituisci stringa vuota.
Lista macro-zone consentite:{macro_list}

Rispondi SOLO in JSON, nel formato:
{{
          "zone_macro": "<una delle macro-zone sopra oppure \"\" se incerto>"
}}

ZONA: {zona_text}
"""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Sei un assistente che classifica quartieri di Barcellona in macro-zone predefinite."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            json=payload
        )
        if r.status_code != 200:
            print(f"❌ AI macro-zone error: {r.text}")
            return ""
        content = r.json()["choices"][0]["message"]["content"]
        parsed = parse_llm_json(content)
        if not isinstance(parsed, dict):
            return ""
        # Tolleranza su chiave/maiuscole
        key = None
        for k in parsed.keys():
            if k.lower() == "zone_macro":
                key = k
                break
        if not key:
            return ""
        value = str(parsed.get(key) or "").strip()
        return value if value in BARCELONA_MACRO_ZONES else ""
    except Exception as e:
        print(f"❌ AI macro-zone call error: {e}")
        return ""

def send_to_notion(data):
    """Invia i dati a Notion. Restituisce l'ID pagina se creato, altrimenti None."""
    titolo = data.get("paraphrased_title", "")
    overview = data.get("overview", "")
    descr = data.get("original_description", "")
    prezzo = data.get("price", "")
    zona = data.get("zone", "")
    zona_macro_result = infer_macro_zone(
        zona,
        titolo=titolo,
        descrizione=descr
    )
    zona_macro = zona_macro_result[0]  # Estrai solo la macro-zona
    zona_matched = zona_macro_result[1]  # Zona che ha causato il match
    if zona_macro:
        print(f"🗺️ Zona_macro '{zona_macro}' dedotta da '{zona_matched}' per zona '{zona}'")
    camere = data.get("rooms", "")
    affidabilita = safe_number(data.get("reliability"))
    motivo = data.get("rating_reason", "")
    link_url = data.get("link", "")
    immagini = data.get("images", [])
    
    # Prendi la prima immagine se disponibile, altrimenti null
    prima_immagine = immagini[0] if immagini else None
    if prima_immagine:
        print(f"🖼️ Saving image for: {titolo[:50]}...")
    
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
                    "paraphrased_title": {"title": [{"text": {"content": titolo}}]},
        "overview": {"rich_text": [{"text": {"content": overview}}]},
        "original_description": {"rich_text": [{"text": {"content": descr}}]},
        "price": {"rich_text": [{"text": {"content": prezzo}}]},
                    "zone": {"rich_text": [{"text": {"content": zona}}]},
        "zone_macro": {"rich_text": [{"text": {"content": zona_macro}}]},
                    "rooms": {"rich_text": [{"text": {"content": camere}}]},
        "reliability": {"number": affidabilita},
        "rating_reason": {"rich_text": [{"text": {"content": motivo}}]},
                    "date_added": {"date": {"start": time.strftime("%Y-%m-%dT%H:%M:%S")}},
        "link": {"url": link_url},
        "images": {"url": prima_immagine},
            "status": {"select": {"name": "active"}}
        }
    }
    res = requests.post("https://api.notion.com/v1/pages", headers=HEADERS_NOTION, json=payload)
    if res.status_code != 200:
        print(f"❌ Notion add error: {res.text}")
        return None
    else:
        page = res.json()
        page_id = page.get("id")
        print(f"✅ Added to Notion: {data['paraphrased_title']} ({page_id})")
        return page_id

def call_openrouter(posts_batch, max_retries=3):
    """Chiama il modello OpenRouter per un batch di post con retry e backoff dinamico."""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Sei un assistente che filtra e analizza annunci immobiliari."},
            {"role": "user", "content": PROMPT_TEMPLATE.format(posts=json.dumps(posts_batch, ensure_ascii=False))}
        ]
    }
    
    current_backoff = INITIAL_BACKOFF_SECONDS
    
    for attempt in range(max_retries):
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
                json=payload
            )
            
            if r.status_code == 429:
                print(f"⏳ Rate limit reached (attempt {attempt + 1}/{max_retries}), waiting {current_backoff} seconds...")
                time.sleep(current_backoff)
                # Aumenta il backoff per il prossimo tentativo
                current_backoff = MAX_BACKOFF_SECONDS
                continue
            elif r.status_code != 200:
                print(f"❌ OpenRouter API error: {r.text}")
                # Aumenta il backoff per il prossimo tentativo
                current_backoff = MAX_BACKOFF_SECONDS
                return None
            
            data = r.json()
            return data["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"❌ OpenRouter call error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {current_backoff} seconds before retry...")
                time.sleep(current_backoff)
                # Aumenta il backoff per il prossimo tentativo
                current_backoff = MAX_BACKOFF_SECONDS
    
            print(f"❌ Failed after {max_retries} attempts")
    return None

def process_rss():
    """Scarica e processa i post RSS da multiple feed."""
    
    # Inizializza sempre la cache (crea file vuoto se non esiste)
    print("🔧 Inizializzazione cache...")
    initial_cache = load_rejected_cache()
    if not os.path.exists(CACHE_FILE):
        save_rejected_cache(initial_cache)
        print(f"✅ Cache file initialized: {os.path.abspath(CACHE_FILE)}")
    else:
        # Aggiorna sempre il timestamp per assicurarsi che Git rilevi cambiamenti
        initial_cache['timestamp'] = datetime.now().isoformat()
        save_rejected_cache(initial_cache)
        print(f"✅ Cache file updated: {os.path.abspath(CACHE_FILE)}")
    
    # Recupera tutti i dati esistenti in una sola chiamata ottimizzata
    print("📋 Loading existing data from database...")
    existing_links, existing_pages = get_existing_data()
    active_pages = [p for p in existing_pages if p.get("status") != "expired"]
    print(f"📋 Loaded {len(active_pages)} active pages for deduplication")
    
    # Carica cache degli URL scartati
    cache_count, avg_age, oldest_age = get_cache_stats()
    print(f"📋 Rejected URLs cache: {cache_count} URLs in memory")
    if cache_count > 0:
        print(f"   📊 Average age: {avg_age:.1f}h, Oldest: {oldest_age:.1f}h")
    
    # Lista dinamica per i nuovi post aggiunti (per deduplicazione intra-batch)
    newly_added_pages = []
    
    total_new_posts = 0
    total_rejected = 0
    
    # Raccoglie i post aggiunti per eventuale fallback AI macro-zone (GLOBALE)
    all_added_posts_for_ai = []
    
    for i, rss_url in enumerate(RSS_URLS, 1):
        print(f"\n📡 Processing RSS feed {i}/{len(RSS_URLS)}: {rss_url}")
        
        try:
            feed = feedparser.parse(rss_url)
            
            # Verifica se il parsing è andato a buon fine
            if feed.bozo:
                print(f"⚠️ RSS feed parsing error {i}: {feed.bozo_exception}")
                continue
                
            if not feed.entries:
                print(f"ℹ️ No posts found in RSS feed {i}")
                continue
                
        except Exception as e:
            print(f"❌ Error accessing RSS feed {i} ({rss_url}): {e}")
            continue
            
        posts = []
        
        # Filtra i post già esistenti e quelli nella cache degli scartati
        for entry in feed.entries:
            link = entry.link
            if link not in existing_links:
                if is_url_rejected(link):
                    print(f"🚫 Post rejected (in cache): {link}")
                    total_rejected += 1
                else:
                    # Usa description se disponibile, altrimenti summary, altrimenti content
                    raw_description = ""
                    if "description" in entry:
                        raw_description = entry.description
                    elif "summary" in entry:
                        raw_description = entry.summary
                    elif "content" in entry and entry.content:
                        raw_description = entry.content[0].value
                    
                    # Pulisci il testo rimuovendo HTML e immagini
                    clean_description = clean_html_from_description(raw_description)
                    
                    # Log della pulizia se c'è differenza significativa
                    if len(raw_description) > len(clean_description) + 50:  # Se è stata rimossa una quantità significativa di HTML
                        print(f"🧹 Cleaned text: {len(raw_description)} → {len(clean_description)} characters for: {entry.title[:50]}...")
                    
                    # Estrai immagini dal post
                    images = extract_all_images(entry)
                    if images:
                        print(f"🖼️ Found {len(images)} images for: {entry.title[:50]}...")
                    
                    posts.append({
                        "title": entry.title,
                        "link": link,
                        "summary": clean_description,  # Usa il testo pulito (censura dopo AI)
                        "images": images
                    })
            else:
                print(f"⏭️ Post already exists, skip: {link}")
        
        if not posts:
            print(f"ℹ️ No new posts to process for feed {i}.")
            continue
            
        print(f"⏳ Parsing RSS feed {i}... Found {len(posts)} new posts to process")

        batch_size = MAX_BATCH
        idx = 0
        new_posts_added = 0
        
        while idx < len(posts):
            current_batch = posts[idx: idx + batch_size]
            print(f"📦 Processing batch of {len(current_batch)} posts (feed {i})...")
            response_text = call_openrouter(current_batch)
            
            # Se response_text è None, potrebbe essere dovuto a rate limiting
            if response_text is None:
                if batch_size > MIN_BATCH:
                    batch_size -= 1
                    print(f"↪ Retry reducing batch to {batch_size}")
                    continue
                else:
                    print("⚠️ Batch impossible to process, skip.")
                    idx += 1
                    batch_size = MAX_BATCH
                    continue
            
            parsed = parse_llm_json(response_text)
            if not parsed:
                if batch_size > MIN_BATCH:
                    batch_size -= 1
                    print(f"↪ Retry reducing batch to {batch_size}")
                    continue
                else:
                    print("⚠️ Batch impossible to process, skip.")
                    idx += 1
                    batch_size = MAX_BATCH
                    continue

            # Se parsed è una lista di risultati
            if isinstance(parsed, list):
                # Combina pagine esistenti + nuove pagine aggiunte per deduplicazione completa
                all_active_pages = active_pages + newly_added_pages
                
                # Lista temporanea per i post rilevanti del batch corrente
                relevant_posts = []
                
                # Prima passata: raccogli tutti i post rilevanti del batch
                for post_data, original_post in zip(parsed, current_batch):
                    if post_data.get("relevant_listing") == "YES":
                        post_data["link"] = original_post["link"]
                        # Censura i dati sensibili dalla descrizione pulita (solo per post rilevanti)
                        censored_description = censor_sensitive_data(original_post["summary"])
                        post_data["original_description"] = censored_description
                        # Aggiungi le immagini dal feed RSS
                        post_data["images"] = original_post.get("images", [])
                        relevant_posts.append(post_data)
                        
                        # Log della censura se sono stati censurati dati sensibili
                        if has_sensitive_data(original_post["summary"]):
                                                    print(f"🔒 Sensitive data censored for: {original_post['title'][:50]}...")
                    else:
                        print(f"❌ Post not relevant: {original_post['title']}")
                        print(f"🔗 URL rejected: {original_post['link']}")
                        # Aggiungi alla cache degli scartati
                        add_to_rejected_cache(original_post['link'], "AI_NOT_RELEVANT")
                        total_rejected += 1
                
                # Seconda passata: deduplicazione intra-batch e inserimento
                
                # Pre-calcola le descrizioni normalizzate per ottimizzazione
                relevant_posts_with_norm = []
                for post_data in relevant_posts:
                    new_descr = post_data.get("original_description", "")
                    post_data["_normalized_desc"] = normalize_text(new_descr)
                    relevant_posts_with_norm.append(post_data)
                
                # Controllo duplicati intra-batch prima di tutto (più veloce)
                unique_posts = []
                for post_data in relevant_posts_with_norm:
                    new_descr = post_data.get("original_description", "")
                    new_descr_norm = post_data["_normalized_desc"]
                    
                    # Controlla duplicati solo con i post già processati in questo batch
                    is_duplicate = False
                    for existing_post in unique_posts:
                        existing_descr_norm = existing_post["_normalized_desc"]
                        if similarity_score(new_descr_norm, existing_descr_norm) >= HIGH_DUP_THRESHOLD:
                            print(f"🔄 Intra-batch duplicate detected, skip: {post_data.get('paraphrased_title', '')[:50]}...")
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        unique_posts.append(post_data)
                
                print(f"📦 Batch reduced from {len(relevant_posts)} to {len(unique_posts)} unique posts")
                
                # Ora processa solo i post unici
                for post_data in unique_posts:
                    new_descr = post_data.get("original_description", "")
                    
                    # Controlla duplicati con pagine esistenti
                    best_page, best_score = find_best_duplicate_optimized(all_active_pages, new_descr, HIGH_DUP_THRESHOLD)
                    
                    # Log per debug deduplicazione
                    if best_score > 0.7:  # Log solo per score alti
                        print(f"🔍 Duplicate check: score {best_score:.3f} for '{post_data.get('paraphrased_title', '')[:30]}...'")
                    
                    if best_page and best_score >= HIGH_DUP_THRESHOLD:
                        # Trovato duplicato forte con pagina esistente, sostituiscila
                        print(f"🔄 Duplicate with existing page detected (score: {best_score:.3f}), replacing...")
                        new_item = {
                            "paraphrased_title": post_data.get("paraphrased_title", ""),
                            "original_description": new_descr,
                            "price": post_data.get("price", ""),
                            "zone": post_data.get("zone", ""),
                                    "zone_macro": infer_macro_zone(
            post_data.get("zone", ""),
            titolo=post_data.get("paraphrased_title", ""),
            descrizione=new_descr
        )[0],  # Estrai solo la macro-zona
                            "rating_reason": post_data.get("rating_reason", ""),
                            "reliability": post_data.get("reliability", None),
                            "overview": post_data.get("overview", ""),
                            "images": post_data.get("images", []),
                            "link": post_data.get("link", ""),
                        }
                        # Crea la nuova pagina
                        new_page_id = send_to_notion(new_item)
                        if new_page_id:
                            # Marca la pagina esistente come scaduta
                            old_page_id = best_page.get("id")
                            mark_status_expired(old_page_id)
                            # Aggiorna cache in RAM per non riproporlo
                            for p in all_active_pages:
                                if p.get("id") == old_page_id:
                                    p["status"] = "expired"
                                    break
                            
                            # Aggiungi la nuova pagina alla lista per deduplicazione futura
                            new_page_data = {
                                "id": new_page_id,
                                "created_time": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                "paraphrased_title": new_item.get("paraphrased_title", ""),
                                "original_description": new_item.get("original_description", ""),
                                "price": new_item.get("price", ""),
                                "zone": new_item.get("zone", ""),
                                "zone_macro": new_item.get("zone_macro", ""),
                                "status": "",
                                "link": new_item.get("link", "")
                            }
                            newly_added_pages.append(new_page_data)
                            new_posts_added += 1
                        else:
                            print("⚠️ New page creation failed, skip duplicate marking")
                    else:
                        # Nessun duplicato forte: inseriamo normalmente
                        page_id = send_to_notion(post_data)
                        if page_id:
                            new_posts_added += 1
                            # Se abbiamo una Zona ma non siamo riusciti a inferire una Zona_macro, tentiamo in coda con AI
                            zona = post_data.get("zone", "")
                            zona_macro_result = infer_macro_zone(
                                zona,
                                titolo=post_data.get("paraphrased_title", ""),
                                descrizione=post_data.get("original_description", "")
                            )
                            zona_macro = zona_macro_result[0]
                            zona_matched = zona_macro_result[1]
                            if zona_macro:
                                print(f"🗺️ Zone_macro '{zona_macro}' inferred from '{zona_matched}' for zone '{zona}'")
                            if zona and not zona_macro:
                                all_added_posts_for_ai.append({
                                    "page_id": page_id,
                                    "zona": zona
                                })
                            # Aggiungi alla lista per confronti successivi
                            new_page_data = {
                                "id": page_id,
                                "created_time": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                "paraphrased_title": post_data.get("paraphrased_title", ""),
                                "original_description": post_data.get("original_description", ""),
                                "price": post_data.get("price", ""),
                                "zone": post_data.get("zone", ""),
                                "zone_macro": zona_macro,
                                "status": "",
                                "link": post_data.get("link", "")
                            }
                            newly_added_pages.append(new_page_data)
                        else:
                            print("⚠️ Creazione pagina fallita")
            else:
                print("⚠️ Risultato inatteso dal modello.")

            idx += batch_size
            batch_size = MAX_BATCH
            # Assicura che ci siano sempre almeno INITIAL_BACKOFF_SECONDS tra le richieste
            print(f"⏳ Waiting {INITIAL_BACKOFF_SECONDS} seconds before next batch...")
            time.sleep(INITIAL_BACKOFF_SECONDS)

        print(f"🎉 Processing completed for feed {i}! Added {new_posts_added} new listings.")
        total_new_posts += new_posts_added

    # Fallback AI GLOBALE: per tutti i post aggiunti con Zona presente ma senza Zona_macro dedotta
    if all_added_posts_for_ai:
        print(f"🧠 GLOBAL AI macro-zone fallback for {len(all_added_posts_for_ai)} new listings without Zone_macro...")
        for item in all_added_posts_for_ai:
            page_id = item["page_id"]
            zona_txt = item["zona"]
            ai_macro = ai_macro_zone_from_zone(zona_txt)
            if ai_macro:
                # aggiorna la pagina Notion con Zona_macro
                try:
                    url = f"https://api.notion.com/v1/pages/{page_id}"
                    payload = {"properties": {"zone_macro": {"rich_text": [{"text": {"content": ai_macro}}]}}}
                    r = requests.patch(url, headers=HEADERS_NOTION, json=payload)
                    if r.status_code == 200:
                        print(f"✅ Zone_macro updated via AI → {ai_macro} for {page_id}")
                    else:
                        print(f"❌ Zone_macro update error via AI for {page_id}: {r.text}")
                except Exception as e:
                    print(f"❌ Zone_macro update exception via AI for {page_id}: {e}")

    print(f"\n🎉 TOTAL PROCESSING COMPLETED!")
    print(f"   📊 Added: {total_new_posts} new listings from {len(RSS_URLS)} RSS feeds")
    print(f"   🚫 Rejected: {total_rejected} posts (saved in cache)")
    final_cache_count, final_avg_age, final_oldest_age = get_cache_stats()
    print(f"   📋 Cache: {final_cache_count} URLs in memory (average age: {final_avg_age:.1f}h)")
    
    # Pulisci le cache in memoria per evitare memory leak
    clear_caches()
    print(f"   🧹 In-memory caches cleared")
    
    # Statistiche performance
    print(f"   ⚡ Performance: Similarity cache: {len(_similarity_cache)} calculations, Text cache: {len(_text_normalization_cache)} normalizations")
    
    # Verifica finale del file cache
    if os.path.exists(CACHE_FILE):
        file_size = os.path.getsize(CACHE_FILE)
        print(f"   ✅ File cache: {CACHE_FILE} ({file_size} bytes)")
    else:
        print(f"   ❌ Cache file NOT found: {CACHE_FILE}")

if __name__ == "__main__":
    process_rss()
