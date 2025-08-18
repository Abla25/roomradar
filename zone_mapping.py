# zone_mapping.py
# Configurazione per il mapping delle zone/quartieri di Barcellona nelle macro-zone

# Macro-zone predefinite di Barcellona e area metropolitana
BARCELONA_MACRO_ZONES = [
    "Ciutat Vella",
    "Eixample", 
    "Gràcia",
    "Horta Guinardó",
    "Les Corts",
    "Nou Barris",
    "Sant Andreu",
    "Sant Martí",
    "Sants-Montjuïc",
    "Sarrià-Sant Gervasi",
    "Badalona",
    "Santa Coloma de Gramenet",
    "L'Hospitalet de Llobregat",
]

# Mapping dettagliato zona/quartiere -> macro-zona
# Ogni macro-zona ha una lista di token (quartieri, aree, sinonimi) che la identificano
MACRO_ZONE_MAPPING = {
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
    ],
}
