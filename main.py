import os
import requests
import json
import time
import feedparser
import re
import unicodedata
from rapidfuzz import fuzz
from zone_mapping import BARCELONA_MACRO_ZONES, MACRO_ZONE_MAPPING

# CONFIGURAZIONE
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL_NAME = "meta-llama/llama-3.3-70b-instruct:free"

RSS_URL = os.environ["RSS_URL"]

MAX_BATCH = 3
MIN_BATCH = 1
BACKOFF_SECONDS = 62

# Soglie similarità per deduplica (setup semplice)
HIGH_DUP_THRESHOLD = 0.93  # sopra questa soglia segniamo direttamente il vecchio come "Scaduto"
AI_CHECK_THRESHOLD_LOW = 0.83  # non usato ora (DB piccolo), ma lasciato per futuro
ENABLE_AI_DUP_CHECK = False

HEADERS_NOTION = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

PROMPT_TEMPLATE = """
Analizza i post seguenti e restituisci un JSON valido per ognuno.
Escludi tutti i post dove qualcuno CERCA una stanza o un appartamento,
o post che non riguardano affitti reali, o post relativi ad affitti brevi per vacanza con prezzi per giornata. Gli unici post rilevanti sono quelli relativi ad inserzioni di camere/abitazioni che vengono messe in affitto.

IMPORTANTE: Per tutti i campi, se l'informazione non è disponibile o non può essere estratta dal post, usa sempre "N/A" come valore. Non lasciare campi vuoti e non usare "Non specificato" o simili.

Per ogni post pertinente, genera un dizionario con:
{{
  "annuncio_rilevante": "SI" o "NO",
  "Titolo_parafrasato": "...",
  "Overview": "...",
  "Descrizione_originale": "...",
  "Prezzo": "..." (usa "N/A" se non disponibile),
  "Zona": "..." (usa "N/A" se non disponibile),
  "Camere": "..." (usa "N/A" se non disponibile),
  "Affidabilita": numero (0-5) (basati sulle informazioni, se sono sufficienti, se l'articolo contiene foto, contatti e non sembri una truffa; 4 e 5 possono essere raggiunti solo se sono presenti foto e non sembri una truffa),
  "Motivo_Rating": "...",
}}
Rispondi SOLO con JSON. Nessun testo aggiuntivo.
POST:
{posts}
"""

def get_existing_links():
    """Recupera tutti i link esistenti dal database Notion."""
    existing_links = set()
    has_more = True
    next_cursor = None
    
    while has_more:
        query_payload = {
            "page_size": 100,
            "filter": {
                "property": "Link",
                "url": {
                    "is_not_empty": True
                }
            }
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
                print(f"❌ Errore recupero link esistenti: {response.text}")
                break
                
            data = response.json()
            
            for page in data.get("results", []):
                link_prop = page.get("properties", {}).get("Link", {})
                if link_prop.get("url"):
                    existing_links.add(link_prop["url"])
            
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
            
        except Exception as e:
            print(f"❌ Errore durante il recupero dei link: {e}")
            break
    
    print(f"📋 Trovati {len(existing_links)} link esistenti nel database")
    return existing_links

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
    text = (text or "").lower()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[\W_]+", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text

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
    a_norm, b_norm = normalize_text(a), normalize_text(b)
    if not a_norm or not b_norm:
        return 0.0
    return fuzz.token_set_ratio(a_norm, b_norm) / 100.0

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

def get_existing_pages():
    """Recupera pagine esistenti con campi utili per il confronto duplicati."""
    pages = []
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
                print(f"❌ Errore recupero pagine esistenti: {response.text}")
                break

            data = response.json()
            for page in data.get("results", []):
                props = page.get("properties", {})
                pages.append({
                    "id": page.get("id"),
                    "created_time": page.get("created_time"),
                    "Titolo_parafrasato": _extract_text_property(props.get("Titolo_parafrasato", {})),
                    "Descrizione_originale": _extract_text_property(props.get("Descrizione_originale", {})),
                    "Prezzo": _extract_text_property(props.get("Prezzo", {})),
                    "Zona": _extract_text_property(props.get("Zona", {})),
                    "Status": _extract_status_name(props.get("Status", {})),
                    "Link": props.get("Link", {}).get("url", "")
                })

            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
        except Exception as e:
            print(f"❌ Errore durante il recupero delle pagine: {e}")
            break

    print(f"📋 Pagine caricate per confronto duplicati: {len(pages)}")
    return pages

def mark_status_scaduto(page_id: str):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": {"Status": {"select": {"name": "Scaduto"}}}}
    res = requests.patch(url, headers=HEADERS_NOTION, json=payload)
    if res.status_code != 200:
        print(f"❌ Errore aggiornamento Status=Scaduto per {page_id}: {res.text}")
    else:
        print(f"🗂️ Impostato Status=Scaduto per pagina {page_id}")

def find_best_duplicate(existing_pages: list, new_descr: str):
    """Ritorna (best_page, best_score) se trova un candidato duplicato, altrimenti (None, 0)."""
    best_page = None
    best_score = 0.0
    for p in existing_pages:
        descr = p.get("Descrizione_originale", "")
        if not descr:
            continue
        score = similarity_score(new_descr, descr)
        if score > best_score:
            best_score = score
            best_page = p
    return best_page, best_score

def ai_same_listing_check(a_post: dict, b_post: dict) -> dict | None:
    """Verifica AI pairwise se due annunci descrivono lo stesso immobile."""
    prompt = f"""
Confronta i due annunci qui sotto. Rispondi SOLO JSON:
{{
  "same_listing": "SI" o "NO",
  "confidence": numero tra 0 e 1,
  "reason": "..."
}}

Annuncio A:
Titolo: {a_post.get("Titolo_parafrasato","")}
Zona: {a_post.get("Zona","")}
Prezzo: {a_post.get("Prezzo","")}
Descrizione: {a_post.get("Descrizione_originale","")}

Annuncio B:
Titolo: {b_post.get("Titolo_parafrasato","")}
Zona: {b_post.get("Zona","")}
Prezzo: {b_post.get("Prezzo","")}
Descrizione: {b_post.get("Descrizione_originale","")}
"""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Sei un assistente che decide se due annunci immobiliari descrivono la stessa stanza/immobile."},
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
            print(f"❌ Errore AI pairwise: {r.text}")
            return None
        content = r.json()["choices"][0]["message"]["content"]
        return parse_llm_json(content)
    except Exception as e:
        print(f"❌ Errore chiamata AI pairwise: {e}")
        return None

def parse_llm_json(raw_text, retries=3):
    """Tenta di parsare JSON da testo grezzo con retry."""
    for attempt in range(retries):
        raw_text = raw_text.strip()
        if not raw_text:
            print(f"⚠️ Risposta vuota. Retry {attempt+1}/{retries}")
            time.sleep(2 ** attempt)
            continue
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            print(f"⚠️ JSON non valido. Retry {attempt+1}/{retries}")
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
  "Zona_macro": "<una delle macro-zone sopra oppure \"\" se incerto>"
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
            print(f"❌ Errore AI macro-zone: {r.text}")
            return ""
        content = r.json()["choices"][0]["message"]["content"]
        parsed = parse_llm_json(content)
        if not isinstance(parsed, dict):
            return ""
        # Tolleranza su chiave/maiuscole
        key = None
        for k in parsed.keys():
            if k.lower() == "zona_macro":
                key = k
                break
        if not key:
            return ""
        value = str(parsed.get(key) or "").strip()
        return value if value in BARCELONA_MACRO_ZONES else ""
    except Exception as e:
        print(f"❌ Errore chiamata AI macro-zone: {e}")
        return ""

def send_to_notion(data):
    """Invia i dati a Notion. Restituisce l'ID pagina se creato, altrimenti None."""
    titolo = data.get("Titolo_parafrasato", "")
    overview = data.get("Overview", "")
    descr = data.get("Descrizione_originale", "")
    prezzo = data.get("Prezzo", "")
    zona = data.get("Zona", "")
    zona_macro_result = infer_macro_zone(
        zona,
        titolo=titolo,
        descrizione=descr
    )
    zona_macro = zona_macro_result[0]  # Estrai solo la macro-zona
    zona_matched = zona_macro_result[1]  # Zona che ha causato il match
    if zona_macro:
        print(f"🗺️ Zona_macro '{zona_macro}' dedotta da '{zona_matched}' per zona '{zona}'")
    camere = data.get("Camere", "")
    affidabilita = safe_number(data.get("Affidabilita"))
    motivo = data.get("Motivo_Rating", "")
    link_url = data.get("link", "")
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Titolo_parafrasato": {"title": [{"text": {"content": titolo}}]},
            "Overview": {"rich_text": [{"text": {"content": overview}}]},
            "Descrizione_originale": {"rich_text": [{"text": {"content": descr}}]},
            "Prezzo": {"rich_text": [{"text": {"content": prezzo}}]},
            "Zona": {"rich_text": [{"text": {"content": zona}}]},
            "Zona_macro": {"rich_text": [{"text": {"content": zona_macro}}]},
            "Camere": {"rich_text": [{"text": {"content": camere}}]},
            "Affidabilita": {"number": affidabilita},
            "Motivo_Rating": {"rich_text": [{"text": {"content": motivo}}]},
            "Data_DB": {"date": {"start": time.strftime("%Y-%m-%dT%H:%M:%S")}},
            "Link": {"url": link_url},
            "Status": {"select": {"name": "Attivo"}}
        }
    }
    res = requests.post("https://api.notion.com/v1/pages", headers=HEADERS_NOTION, json=payload)
    if res.status_code != 200:
        print(f"❌ Errore aggiunta Notion: {res.text}")
        return None
    else:
        page = res.json()
        page_id = page.get("id")
        print(f"✅ Aggiunto su Notion: {data['Titolo_parafrasato']} ({page_id})")
        return page_id

def call_openrouter(posts_batch, max_retries=3):
    """Chiama il modello OpenRouter per un batch di post con retry e backoff fisso."""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Sei un assistente che filtra e analizza annunci immobiliari."},
            {"role": "user", "content": PROMPT_TEMPLATE.format(posts=json.dumps(posts_batch, ensure_ascii=False))}
        ]
    }
    
    for attempt in range(max_retries):
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
                json=payload
            )
            
            if r.status_code == 429:
                print(f"⏳ Rate limit raggiunto (tentativo {attempt + 1}/{max_retries}), attendo {BACKOFF_SECONDS} secondi...")
                time.sleep(BACKOFF_SECONDS)
                continue
            elif r.status_code != 200:
                print(f"❌ Errore API OpenRouter: {r.text}")
                return None
            
            data = r.json()
            return data["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"❌ Errore chiamata OpenRouter (tentativo {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Attendo {BACKOFF_SECONDS} secondi prima del retry...")
                time.sleep(BACKOFF_SECONDS)
    
    print(f"❌ Fallito dopo {max_retries} tentativi")
    return None

def process_rss():
    """Scarica e processa i post RSS."""
    # Recupera i link esistenti all'inizio
    existing_links = get_existing_links()
    
    feed = feedparser.parse(RSS_URL)
    posts = []
    
    # Filtra i post già esistenti prima di elaborarli
    for entry in feed.entries:
        link = entry.link
        if link not in existing_links:
            posts.append({
                "title": entry.title,
                "link": link,
                "summary": entry.summary if "summary" in entry else ""
            })
        else:
            print(f"⏭️ Post già esistente, skip: {link}")
    
    if not posts:
        print("ℹ️ Nessun nuovo post da elaborare.")
        return
        
    print(f"⏳ Parsing RSS... Trovati {len(posts)} nuovi post da elaborare")

    batch_size = MAX_BATCH
    idx = 0
    new_posts_added = 0
    # Raccoglie i post aggiunti per eventuale fallback AI macro-zone
    added_posts_for_ai = []
    
    while idx < len(posts):
        current_batch = posts[idx: idx + batch_size]
        print(f"📦 Elaboro batch da {len(current_batch)} post...")
        response_text = call_openrouter(current_batch)
        
        # Se response_text è None, potrebbe essere dovuto a rate limiting
        if response_text is None:
            if batch_size > MIN_BATCH:
                batch_size -= 1
                print(f"↪ Retry riducendo batch a {batch_size}")
                continue
            else:
                print("⚠️ Batch impossibile da elaborare, skip.")
                idx += 1
                batch_size = MAX_BATCH
                continue
        
        parsed = parse_llm_json(response_text)
        if not parsed:
            if batch_size > MIN_BATCH:
                batch_size -= 1
                print(f"↪ Retry riducendo batch a {batch_size}")
                continue
            else:
                print("⚠️ Batch impossibile da elaborare, skip.")
                idx += 1
                batch_size = MAX_BATCH
                continue

        # Se parsed è una lista di risultati
        if isinstance(parsed, list):
            # Carica pagine esistenti (non "Scaduto") una volta per batch
            existing_pages = get_existing_pages()
            active_pages = [p for p in existing_pages if p.get("Status") != "Scaduto"]

            for post_data, original_post in zip(parsed, current_batch):
                if post_data.get("annuncio_rilevante") == "SI":
                    post_data["link"] = original_post["link"]

                    # 1) dedupe intra-batch semplice: usa la descrizione
                    new_descr = post_data.get("Descrizione_originale", "")
                    best_page, best_score = find_best_duplicate(active_pages, new_descr)

                    if best_page and best_score >= HIGH_DUP_THRESHOLD:
                        # Trovato duplicato forte: manteniamo quello più recente
                        new_item = {
                            "Titolo_parafrasato": post_data.get("Titolo_parafrasato", ""),
                            "Descrizione_originale": new_descr,
                            "Prezzo": post_data.get("Prezzo", ""),
                            "Zona": post_data.get("Zona", ""),
                            "Zona_macro": infer_macro_zone(
                                post_data.get("Zona", ""),
                                titolo=post_data.get("Titolo_parafrasato", ""),
                                descrizione=new_descr
                            )[0],  # Estrai solo la macro-zona
                            "Motivo_Rating": post_data.get("Motivo_Rating", ""),
                            "Affidabilita": post_data.get("Affidabilita", None),
                            "Overview": post_data.get("Overview", ""),
                            "link": post_data.get("link", ""),
                        }
                        # Crea la nuova pagina
                        new_page_id = send_to_notion(new_item)
                        if new_page_id:
                            # Decidi chi è più vecchio: usa created_time disponibile su best_page
                            old_page_id = best_page.get("id")
                            # Confronto semplice: se best_page ha created_time < ora corrente → è più vecchio, marchiamo quello
                            # In assenza di created_time della nuova pagina, consideriamo best_page come quello vecchio
                            mark_status_scaduto(old_page_id)
                            # Aggiorna cache in RAM per non riproporlo
                            for p in active_pages:
                                if p.get("id") == old_page_id:
                                    p["Status"] = "Scaduto"
                                    break
                            new_posts_added += 1
                        else:
                            print("⚠️ Creazione nuova pagina fallita, skip marcatura duplicati")
                    else:
                        # Nessun duplicato forte: inseriamo normalmente
                        page_id = send_to_notion(post_data)
                        if page_id:
                            new_posts_added += 1
                            # Se abbiamo una Zona ma non siamo riusciti a inferire una Zona_macro, tentiamo in coda con AI
                            zona = post_data.get("Zona", "")
                            zona_macro_result = infer_macro_zone(
                                zona,
                                titolo=post_data.get("Titolo_parafrasato", ""),
                                descrizione=post_data.get("Descrizione_originale", "")
                            )
                            zona_macro = zona_macro_result[0]
                            zona_matched = zona_macro_result[1]
                            if zona_macro:
                                print(f"🗺️ Zona_macro '{zona_macro}' dedotta da '{zona_matched}' per zona '{zona}'")
                            if zona and not zona_macro:
                                added_posts_for_ai.append({
                                    "page_id": page_id,
                                    "zona": zona
                                })
                            # Aggiungi alla lista per confronti successivi in questo batch
                            active_pages.append({
                                "id": page_id,
                                "created_time": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                "Titolo_parafrasato": post_data.get("Titolo_parafrasato", ""),
                                "Descrizione_originale": post_data.get("Descrizione_originale", ""),
                                "Prezzo": post_data.get("Prezzo", ""),
                                "Zona": post_data.get("Zona", ""),
                                "Zona_macro": zona_macro,
                                "Status": "",
                                "Link": post_data.get("link", "")
                            })
                        else:
                            print("⚠️ Creazione pagina fallita")
                else:
                    print(f"❌ Post non rilevante: {original_post['title']}")
        else:
            print("⚠️ Risultato inatteso dal modello.")

        idx += batch_size
        batch_size = MAX_BATCH
        # Assicura che ci siano sempre almeno BACKOFF_SECONDS tra le richieste
        print(f"⏳ Attendo {BACKOFF_SECONDS} secondi prima del prossimo batch...")
        time.sleep(BACKOFF_SECONDS)

    # Fallback AI: per i soli post aggiunti con Zona presente ma senza Zona_macro dedotta
    if added_posts_for_ai:
        print(f"🧠 Fallback AI macro-zone per {len(added_posts_for_ai)} nuovi annunci senza Zona_macro…")
        for item in added_posts_for_ai:
            page_id = item["page_id"]
            zona_txt = item["zona"]
            ai_macro = ai_macro_zone_from_zone(zona_txt)
            if ai_macro:
                # aggiorna la pagina Notion con Zona_macro
                try:
                    url = f"https://api.notion.com/v1/pages/{page_id}"
                    payload = {"properties": {"Zona_macro": {"rich_text": [{"text": {"content": ai_macro}}]}}}
                    r = requests.patch(url, headers=HEADERS_NOTION, json=payload)
                    if r.status_code == 200:
                        print(f"✅ Aggiornata Zona_macro via AI → {ai_macro} per {page_id}")
                    else:
                        print(f"❌ Errore update Zona_macro via AI per {page_id}: {r.text}")
                except Exception as e:
                    print(f"❌ Eccezione update Zona_macro via AI per {page_id}: {e}")
    
    print(f"🎉 Elaborazione completata! Aggiunti {new_posts_added} nuovi annunci.")

if __name__ == "__main__":
    process_rss()
