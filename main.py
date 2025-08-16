import os
import requests
import json
import time
import feedparser

# CONFIGURAZIONE
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL_NAME = "meta-llama/llama-3.3-70b-instruct:free"

RSS_URL = os.environ["RSS_URL"]

MAX_BATCH = 3
MIN_BATCH = 1
BACKOFF_SECONDS = 32

HEADERS_NOTION = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Prompt migliorato per eliminare post di ricerca camere
PROMPT_TEMPLATE = """
Analizza i post seguenti e restituisci un JSON valido per ognuno.
Escludi tutti i post dove qualcuno CERCA una stanza o un appartamento,
o post che non riguardano affitti reali. Gli unici post rilevanti sono quelli relativi ad inserzioni di camere/abitazioni che vengono messe in affitto.

Per ogni post pertinente, genera un dizionario con:
{{
  "annuncio_rilevante": "SI" o "NO",
  "Titolo_parafrasato": "...",
  "Overview": "...",
  "Descrizione_originale": "...",
  "Prezzo": "...",
  "Zona": "...",
  "Camere": "...",
  "Affidabilita" (basati sulle informazioni, se sono sufficienti, se l'articolo contiene foto, contatti e non sembri una truffa,...): numero (0-5),
  "Motivo_Rating": "...",
  "Data_Pubblicazione": data ISO 8601 (la trovi nella sezione del file xml relativa a ciascun post tra i tag <pubDate>),
}}
Rispondi SOLO con JSON. Nessun testo aggiuntivo.
POST:
{posts}
"""


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

def send_to_notion(data):
    """Invia i dati a Notion."""
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Titolo_parafrasato": {"title": [{"text": {"content": data["Titolo_parafrasato"]}}]},
            "Overview": {"rich_text": [{"text": {"content": data["Overview"]}}]},
            "Descrizione_originale": {"rich_text": [{"text": {"content": data["Descrizione_originale"]}}]},
            "Prezzo": {"rich_text": [{"text": {"content": data["Prezzo"]}}]},
            "Zona": {"rich_text": [{"text": {"content": data["Zona"]}}]},
            "Camere": {"rich_text": [{"text": {"content": data["Camere"]}}]},
            "Affidabilita": {"number": float(data["Affidabilita"]) if data["Affidabilita"] else None},
            "Motivo_Rating": {"rich_text": [{"text": {"content": data["Motivo_Rating"]}}]},
            "Data_Pubblicazione": {"date": {"start": data["Data_Pubblicazione"]}},
            "Link": {"url": data.get("link", "")}
        }
    }
    res = requests.post("https://api.notion.com/v1/pages", headers=HEADERS_NOTION, json=payload)
    if res.status_code != 200:
        print(f"❌ Errore aggiunta Notion: {res.text}")
    else:
        print(f"✅ Aggiunto su Notion: {data['Titolo_parafrasato']}")

def call_openrouter(posts_batch):
    """Chiama il modello OpenRouter per un batch di post."""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Sei un assistente che filtra e analizza annunci immobiliari."},
            {"role": "user", "content": PROMPT_TEMPLATE.format(posts=json.dumps(posts_batch, ensure_ascii=False))}
        ]
    }
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            json=payload
        )
        if r.status_code != 200:
            print(f"❌ Errore API OpenRouter: {r.text}")
            return None
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Errore chiamata OpenRouter: {e}")
        return None

def process_rss():
    """Scarica e processa i post RSS."""
    feed = feedparser.parse(RSS_URL)
    posts = []
    for entry in feed.entries:
        posts.append({
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary if "summary" in entry else ""
        })
    print(f"⏳ Parsing RSS... Trovati {len(posts)} post")

    batch_size = MAX_BATCH
    idx = 0
    while idx < len(posts):
        current_batch = posts[idx: idx + batch_size]
        print(f"📦 Elaboro batch da {len(current_batch)} post...")
        response_text = call_openrouter(current_batch)
        parsed = parse_llm_json(response_text) if response_text else None

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
            for post_data, original_post in zip(parsed, current_batch):
                if post_data.get("annuncio_rilevante") == "SI":
                    post_data["link"] = original_post["link"]
                    send_to_notion(post_data)
                else:
                    print(f"❌ Post non rilevante: {original_post['link']}")
        else:
            print("⚠️ Risultato inatteso dal modello.")

        idx += batch_size
        batch_size = MAX_BATCH
        time.sleep(BACKOFF_SECONDS)

if __name__ == "__main__":
    process_rss()
