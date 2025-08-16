// fetch-listings.js
const fs = require('fs');
const path = require('path');

const NOTION_API_KEY = process.env.NOTION_API_KEY;
const NOTION_DATABASE_ID = process.env.NOTION_DATABASE_ID;

async function fetchListings() {
    try {
        const fetch = (await import('node-fetch')).default;
        
        const response = await fetch(`https://api.notion.com/v1/databases/${NOTION_DATABASE_ID}/query`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${NOTION_API_KEY}`,
                'Content-Type': 'application/json',
                'Notion-Version': '2022-06-28'
            },
            body: JSON.stringify({
                page_size: 100
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const listings = data.results.map(page => parseNotionPage(page));
        
        // Crea directory public se non esiste
        if (!fs.existsSync('public')) {
            fs.mkdirSync('public');
        }
        
        // Salva i dati
        fs.writeFileSync('public/listings.json', JSON.stringify(listings, null, 2));
        
        // Copia l'HTML template modificato
        const htmlTemplate = fs.readFileSync('template.html', 'utf8');
        const finalHtml = htmlTemplate.replace(
            '// PLACEHOLDER_FOR_DATA',
            `const allListings = ${JSON.stringify(listings, null, 2)};`
        );
        
        fs.writeFileSync('public/index.html', finalHtml);
        
        console.log(`✅ Salvati ${listings.length} annunci`);
        
    } catch (error) {
        console.error('❌ Errore:', error);
        process.exit(1);
    }
}

function parseNotionPage(page) {
    const props = page.properties;
    return {
        id: page.id,
        title: props.Titolo_parafrasato?.title?.[0]?.text?.content || 'Titolo non disponibile',
        overview: props.Overview?.rich_text?.[0]?.text?.content || '',
        description: props.Descrizione_originale?.rich_text?.[0]?.text?.content || '',
        price: props.Prezzo?.rich_text?.[0]?.text?.content || '',
        zone: props.Zona?.rich_text?.[0]?.text?.content || '',
        rooms: props.Camere?.rich_text?.[0]?.text?.content || '',
        reliability: props.Affidabilita?.number || 0,
        reliabilityReason: props.Motivo_Rating?.rich_text?.[0]?.text?.content || '',
        datePublished: props.Data_Pubblicazione?.date?.start || '',
        dateAdded: props.Data_DB?.date?.start || '',
        link: props.Link?.url || ''
    };
}

fetchListings();
