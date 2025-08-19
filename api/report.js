// api/report.js - API endpoint per Vercel
// Gestisce le segnalazioni e incrementa il contatore nel database Notion

module.exports = async function handler(req, res) {
  // Solo metodo POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { listingId, title, link } = req.body;

    // Validazione input
    if (!listingId || !title || !link) {
      return res.status(400).json({ 
        error: 'Missing required fields: listingId, title, link' 
      });
    }

    // Configurazione Notion
    const NOTION_API_KEY = process.env.NOTION_API_KEY;
    const NOTION_DATABASE_ID = process.env.NOTION_DATABASE_ID;

    if (!NOTION_API_KEY || !NOTION_DATABASE_ID) {
      console.error('Missing Notion environment variables');
      return res.status(500).json({ error: 'Server configuration error' });
    }

    // 1. Prima trova la pagina Notion per questo annuncio
    const searchResponse = await fetch(`https://api.notion.com/v1/databases/${NOTION_DATABASE_ID}/query`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${NOTION_API_KEY}`,
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
      },
      body: JSON.stringify({
        filter: {
          property: 'Link',
          url: {
            equals: link
          }
        }
      })
    });

    if (!searchResponse.ok) {
      const errorText = await searchResponse.text();
      console.error('Notion search error:', searchResponse.status, errorText);
      return res.status(500).json({ error: 'Failed to find listing in database' });
    }

    const searchResult = await searchResponse.json();
    
    if (!searchResult.results || searchResult.results.length === 0) {
      console.error('Listing not found:', link);
      return res.status(404).json({ error: 'Listing not found in database' });
    }

    const pageId = searchResult.results[0].id;
    const currentReports = searchResult.results[0].properties?.Segnalazioni?.number || 0;

    // 2. Incrementa il contatore delle segnalazioni
    const updateResponse = await fetch(`https://api.notion.com/v1/pages/${pageId}`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${NOTION_API_KEY}`,
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
      },
      body: JSON.stringify({
        properties: {
          'Segnalazioni': {
            number: currentReports + 1
          }
        }
      })
    });

    if (!updateResponse.ok) {
      const errorText = await updateResponse.text();
      console.error('Notion update error:', updateResponse.status, errorText);
      return res.status(500).json({ error: 'Failed to update listing' });
    }

    // 3. Log della segnalazione
    console.log(`✅ Segnalazione registrata:`, {
      listingId,
      title: title.substring(0, 50) + '...',
      link,
      pageId,
      oldCount: currentReports,
      newCount: currentReports + 1,
      timestamp: new Date().toISOString()
    });

    // 4. Risposta di successo
    return res.status(200).json({
      success: true,
      message: 'Segnalazione registrata con successo',
      data: {
        listingId,
        pageId,
        reportsCount: currentReports + 1
      }
    });

  } catch (error) {
    console.error('❌ Errore API segnalazioni:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      message: error.message 
    });
  }
}
