# Configurazione Multiple RSS Feeds

Il bot ora supporta l'elaborazione di più feed RSS contemporaneamente. Ci sono diversi modi per configurare gli URL dei feed RSS nei secrets di GitHub.

## Metodi di Configurazione

### 1. Array JSON (Raccomandato)
Definisci una variabile `RSS_URLS` nei secrets di GitHub con un array JSON di URL:

```json
[
  "https://feed1.example.com/rss",
  "https://feed2.example.com/rss",
  "https://feed3.example.com/rss"
]
```

### 2. Variabili Separate
Definisci variabili separate per ogni feed:

- `RSS_URL_1`: https://feed1.example.com/rss
- `RSS_URL_2`: https://feed2.example.com/rss
- `RSS_URL_3`: https://feed3.example.com/rss

### 3. Compatibilità Legacy
Se hai già configurato un singolo `RSS_URL`, continuerà a funzionare.

## Priorità di Configurazione

Il sistema controlla le configurazioni in questo ordine:

1. **RSS_URLS** (array JSON) - Priorità massima
2. **RSS_URL** (singolo URL) - Compatibilità legacy
3. **RSS_URL_1, RSS_URL_2, ...** - Variabili separate

## Esempi di Configurazione

### GitHub Secrets - Metodo Array JSON
```
RSS_URLS = ["https://feed1.com/rss", "https://feed2.com/rss"]
```

### GitHub Secrets - Metodo Variabili Separate
```
RSS_URL_1 = https://feed1.com/rss
RSS_URL_2 = https://feed2.com/rss
RSS_URL_3 = https://feed3.com/rss
```

## Vantaggi

- **Elaborazione parallela**: Ogni feed viene processato separatamente
- **Deduplicazione cross-feed**: I duplicati vengono rilevati anche tra feed diversi
- **Gestione errori**: Se un feed fallisce, gli altri continuano a funzionare
- **Logging dettagliato**: Ogni feed ha i suoi log separati

## Note Importanti

- Ogni feed viene processato completamente prima di passare al successivo
- I link vengono controllati globalmente per evitare duplicati tra feed diversi
- Il sistema mantiene la compatibilità con la configurazione esistente
- Se nessun URL è configurato, il bot si fermerà con un errore chiaro
