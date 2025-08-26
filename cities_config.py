# cities_config.py
# Configurazione centralizzata per il supporto multi-città

import os
from typing import Dict, List, Optional

class CityConfig:
    def __init__(self, 
                 name: str,
                 display_name: str,
                 notion_database_id: str,
                 macro_zones: List[str],
                 zone_mapping: Dict[str, List[str]],
                 data_file: str = None,
                 rss_urls: List[str] = None):
        self.name = name
        self.display_name = display_name
        self.notion_database_id = notion_database_id
        self.macro_zones = macro_zones
        self.zone_mapping = zone_mapping
        self.data_file = data_file or f"public/data_{name}.json"
        self.cache_file = f"rejected_urls_cache_{name}.json"
        self.rss_urls = rss_urls or []
    
    def get_rss_urls(self) -> List[str]:
        """Restituisce tutti i feed RSS disponibili per questa città"""
        urls = []
        # Cerca feed RSS specifici per città (RSS_URL_CITY_1, RSS_URL_CITY_2, etc.)
        i = 1
        while True:
            env_var = f"RSS_URL_{self.name.upper()}_{i}"
            url = os.environ.get(env_var, "")
            if not url:
                break
            urls.append(url)
            i += 1
        
        return urls

# Configurazione delle città
CITIES = {
    "barcelona": CityConfig(
        name="barcelona",
        display_name="Barcelona",
        notion_database_id=os.environ.get("NOTION_DATABASE_ID_BARCELONA", os.environ.get("NOTION_DATABASE_ID")),
        macro_zones=[
            "Ciutat Vella", "Eixample", "Gràcia", "Horta Guinardó", "Les Corts",
            "Nou Barris", "Sant Andreu", "Sant Martí", "Sants-Montjuïc",
            "Sarrià-Sant Gervasi", "Badalona", "Santa Coloma de Gramenet",
            "L'Hospitalet de Llobregat"
        ],
        rss_urls=[],  # I feed RSS vengono caricati dinamicamente da get_rss_urls()
        zone_mapping={
            "Ciutat Vella": [
                "ciutat vella", "barri gotic", "el gotic", "gotic", "el born", "born",
                "la ribera", "ribera", "sant pere", "santa caterina", "barceloneta", "el raval", "raval"
            ],
            "Eixample": [
                "eixample", "dreta de l eixample", "dreta de leixample", "esquerra de l eixample",
                "esquerra de leixample", "sagrada familia", "fort pienc", "sant antoni"
            ],
            "Gràcia": [
                "gracia", "vila de gracia", "camp d en grassot", "vallcarca", "el coll", 
                "camp d en grassot i grcia nova", "gracia nova"
            ],
            "Horta Guinardó": [
                "horta", "guinardo", "el carmel", "can baro", "vall d hebron", "montbau", 
                "la font d en fargues"
            ],
            "Les Corts": [
                "les corts", "pedralbes", "la maternitat i sant ramon", "sant ramon"
            ],
            "Nou Barris": [
                "nou barris", "porta", "prosperitat", "vilapicina", "canyelles", "la guineueta", 
                "ciutat meridiana", "trinitat nova", "torre baro", "les roquetes"
            ],
            "Sant Andreu": [
                "sant andreu", "la sagrera", "trinitat vella", "bon pastor", "baro de viver", "navas"
            ],
            "Sant Martí": [
                "sant marti", "poblenou", "el poblenou", "diagonal mar", "el besos i el maresme", 
                "besos", "el clot", "clot", "camp de l arpa", "camp de l arpa del clot", 
                "vila olimpica", "provençals del poblenou", "provenals del poblenou", "22@"
            ],
            "Sants-Montjuïc": [
                "sants", "hostafrancs", "poble sec", "badal", "la marina", "montjuic", "zona franca"
            ],
            "Sarrià-Sant Gervasi": [
                "sarria", "les tres torres", "sant gervasi", "galvany", "la bonanova", "bonanova", 
                "vallvidrera", "tibidabo", "les planes"
            ],
            "Badalona": [
                "badalona", "badal", "can bofarull", "can roca i roca", "casagemes", "canyet", 
                "dalt la villa", "la salut", "morera", "progres", "remei", "sant roc", "sant roc de badalona"
            ],
            "Santa Coloma de Gramenet": [
                "santa coloma de gramenet", "santa coloma", "can peixauet", "fondo", "la salut", 
                "morro de nou", "sant roc", "sant roc de santa coloma", "singuerlin"
            ],
            "L'Hospitalet de Llobregat": [
                "l hospitalet de llobregat", "l hospitalet", "hospitalet", "bellvitge", "can serra", 
                "centre", "collblanc", "el gornal", "la florida", "la marina", "la torrassa", 
                "pubilla cases", "sant josep", "santa eulalia"
            ]
        }
    ),
    
    "roma": CityConfig(
        name="roma",
        display_name="Rome",
        notion_database_id=os.environ.get("NOTION_DATABASE_ID_ROMA"),
        macro_zones=[
            "Centro Storico", "Trastevere", "Testaccio", "Monti", "Esquilino",
            "Pigneto", "San Lorenzo", "Parioli", "Flaminio", "Prati",
            "Vaticano", "Aurelio", "Gianicolense", "Monteverde", "Ostiense",
            "Ardeatino", "Appio Latino", "Tuscolano", "Colli Albani", "Eur"
        ],
        rss_urls=[],  # I feed RSS vengono caricati dinamicamente da get_rss_urls()
        zone_mapping={
            "Centro Storico": [
                "centro storico", "piazza navona", "campo de fiori", "pantheon", "piazza venezia",
                "fori imperiali", "colosseo", "foro romano", "palatino", "circo massimo"
            ],
            "Trastevere": [
                "trastevere", "santa maria in trastevere", "piazza santa cecilia", "viale trastevere"
            ],
            "Testaccio": [
                "testaccio", "monte testaccio", "piazza testaccio", "via marmorata"
            ],
            "Monti": [
                "monti", "rione monti", "via nazionale", "via cavour", "piazza della madonna dei monti"
            ],
            "Esquilino": [
                "esquilino", "piazza vittorio", "via merulana", "via dello statuto", "termini"
            ],
            "Pigneto": [
                "pigneto", "via del pigneto", "via casilina", "via prenestina"
            ],
            "San Lorenzo": [
                "san lorenzo", "via tiburtina", "piazza dell immacolata", "via dei sabelli"
            ],
            "Parioli": [
                "parioli", "via archimede", "via bruxelles", "via orlando", "villa borghese"
            ],
            "Flaminio": [
                "flaminio", "piazza del popolo", "via flaminia", "piazzale flaminio", "villa glori"
            ],
            "Prati": [
                "prati", "via cola di rienzo", "via ottaviano", "piazza risorgimento", "borgo"
            ],
            "Vaticano": [
                "vaticano", "borgo pio", "via della conciliazione", "piazza san pietro"
            ],
            "Aurelio": [
                "aurelio", "via aurelia", "via della pineta sacchetti", "villa doria pamphilj"
            ],
            "Gianicolense": [
                "gianicolense", "monteverde vecchio", "via gianicolense", "piazza san cosimato"
            ],
            "Monteverde": [
                "monteverde", "monteverde nuovo", "via carini", "piazza santa maria della luce"
            ],
            "Ostiense": [
                "ostiense", "via ostiense", "garbatella", "san paolo", "basilica san paolo"
            ],
            "Ardeatino": [
                "ardeatino", "via ardeatina", "via appia antica", "catacombe", "quartiere ardeatino"
            ],
            "Appio Latino": [
                "appio latino", "via appia nuova", "piazza tuscolo", "via latina"
            ],
            "Tuscolano": [
                "tuscolano", "via tuscolana", "cinecittà", "don bosco", "appio claudio"
            ],
            "Colli Albani": [
                "colli albani", "via appia nuova", "via tuscolana", "quartiere colli albani"
            ],
            "Eur": [
                "eur", "europe", "via cristoforo colombo", "piazza marconi", "laghetto dell eur"
            ]
        }
    )
}

def get_city_config(city_name: str) -> Optional[CityConfig]:
    """Restituisce la configurazione per una città specifica"""
    return CITIES.get(city_name.lower())

def get_available_cities() -> List[str]:
    """Restituisce la lista delle città disponibili"""
    return list(CITIES.keys())

def get_city_display_names() -> Dict[str, str]:
    """Restituisce un dizionario con i nomi di visualizzazione delle città"""
    return {city: config.display_name for city, config in CITIES.items()}

def get_default_city() -> str:
    """Restituisce la città di default (Barcelona)"""
    return "barcelona"

# Funzioni helper per compatibilità con il codice esistente
def get_current_city() -> str:
    """Restituisce la città corrente dall'ambiente o dal default"""
    # Prima controlla se c'è una variabile CITY nell'ambiente (per processing manuale)
    city_from_env = os.environ.get("CITY")
    if city_from_env and city_from_env.lower() in CITIES:
        return city_from_env.lower()
    
    # Altrimenti usa la città di default
    return get_default_city()

def get_macro_zones_for_city(city_name: str = None) -> List[str]:
    """Restituisce le macro-zone per una città specifica"""
    city = city_name or get_current_city()
    config = get_city_config(city)
    return config.macro_zones if config else []

def get_zone_mapping_for_city(city_name: str = None) -> Dict[str, List[str]]:
    """Restituisce il mapping delle zone per una città specifica"""
    city = city_name or get_current_city()
    config = get_city_config(city)
    return config.zone_mapping if config else {}

def get_rss_urls_for_city(city_name: str = None) -> List[str]:
    """Restituisce i feed RSS per una città specifica"""
    city = city_name or get_current_city()
    config = get_city_config(city)
    if config:
        return config.get_rss_urls()
    return []

def get_all_rss_urls() -> Dict[str, List[str]]:
    """Restituisce tutti i feed RSS per tutte le città"""
    result = {}
    for city_name, config in CITIES.items():
        urls = config.get_rss_urls()
        if urls:
            result[city_name] = urls
    return result
