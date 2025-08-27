// scripts/fetch_notion.js
// Legge Notion con la chiave dai Secrets e scrive public/data.json

import { writeFile, mkdir, readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";



const NOTION_KEY = process.env.NOTION_API_KEY;

// Supporto multi-città
const CITY = process.env.CITY || "barcelona";
const DB_ID = process.env[`NOTION_DATABASE_ID_${CITY.toUpperCase()}`] || process.env.NOTION_DATABASE_ID;

if (!NOTION_KEY || !DB_ID) {
  console.error(`❌ Mancano NOTION_API_KEY o NOTION_DATABASE_ID per la città ${CITY}`);
  console.error(`🔍 Debug info:`);
  console.error(`   - NOTION_API_KEY: ${NOTION_KEY ? '✅ Presente' : '❌ Mancante'}`);
  console.error(`   - NOTION_DATABASE_ID_${CITY.toUpperCase()}: ${process.env[`NOTION_DATABASE_ID_${CITY.toUpperCase()}`] ? '✅ Presente' : '❌ Mancante'}`);
  console.error(`   - NOTION_DATABASE_ID (fallback): ${process.env.NOTION_DATABASE_ID ? '✅ Presente' : '❌ Mancante'}`);
  console.error(`   - DB_ID finale: ${DB_ID || '❌ Non trovato'}`);
  process.exit(1);
}

console.log(`🏙️ Processing city: ${CITY}`);
console.log(`📊 Database ID: ${DB_ID}`);

async function fetchAllPages() {
  const results = [];
  let has_more = true;
  let next_cursor = undefined;
  let pageCount = 0;

  console.log(`🔍 Fetching pages from database: ${DB_ID}`);

  while (has_more) {
    pageCount++;
    const body = {
      page_size: 100,
      ...(next_cursor ? { start_cursor: next_cursor } : {})
    };

    console.log(`📄 Fetching page ${pageCount}...`);

    try {
      const r = await fetch(`https://api.notion.com/v1/databases/${DB_ID}/query`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${NOTION_KEY}`,
          "Content-Type": "application/json",
          "Notion-Version": "2022-06-28"
        },
        body: JSON.stringify(body)
      });

      if (!r.ok) {
        const t = await r.text();
        console.error(`❌ Notion API Error ${r.status}: ${t}`);
        throw new Error(`Notion API ${r.status}: ${t}`);
      }

      const json = await r.json();
      console.log(`✅ Page ${pageCount}: Found ${json.results.length} results`);
      
      results.push(...json.results);
      has_more = json.has_more;
      next_cursor = json.next_cursor;
    } catch (error) {
      console.error(`❌ Error fetching page ${pageCount}:`, error.message);
      throw error;
    }
  }
  
  console.log(`🎉 Total pages fetched: ${pageCount}, Total results: ${results.length}`);
  return results;
}

// Mappa le proprietà Notion → struttura usata dal tuo frontend
function parseNotionPage(page) {
  const props = page.properties || {};

  const get = (p, type, path) => {
    try {
      if (type === "title") return props[p]?.title?.[0]?.text?.content || "";
      if (type === "rich") return props[p]?.rich_text?.[0]?.text?.content || "";
      if (type === "number") return props[p]?.number ?? null;
      if (type === "date") return props[p]?.date?.start || "";
      if (type === "url") return props[p]?.url || "";
      if (type === "select") return props[p]?.select?.name || "";
      return "";
    } catch {
      return "";
    }
  };

  return {
    id: page.id,
    title: get("paraphrased_title", "title"),
    overview: get("overview", "rich"),
    description: get("original_description", "rich"),
    price: get("price", "rich"),
    zone: get("zone", "rich"),
    zoneMacro: get("zone_macro", "rich"),
    rooms: get("rooms", "rich"),
    reliability: get("reliability", "number") || 0,
    reliabilityReason: get("rating_reason", "rich"),
    datePublished: get("date_published", "date"),
    dateAdded: get("date_added", "date"),
    link: get("link", "url"),
    status: get("status", "select"),
    imageUrl: get("images", "url")
  };
}

// Funzione per leggere il contatore totale dal file cache Python
async function getTotalRejectedCount() {
  const cacheFilePath = path.join(process.cwd(), `rejected_urls_cache_${CITY}.json`);
  
  try {
    if (existsSync(cacheFilePath)) {
      const cacheContent = await readFile(cacheFilePath, "utf-8");
      const cacheData = JSON.parse(cacheContent);
      return cacheData.total_rejected_count || 0;
    }
  } catch (error) {
    console.warn(`⚠️ Could not read rejected URLs cache for ${CITY}:`, error.message);
  }
  
  return 0; // Default se il file non esiste o c'è un errore
}

async function main() {
  try {
    console.log(`🚀 Starting fetch for ${CITY}...`);
    console.log(`📊 Database ID: ${DB_ID}`);
    
    // Verifica che il database ID sia valido (non vuoto e formato corretto)
    if (!DB_ID || DB_ID === 'undefined' || DB_ID === 'null' || DB_ID.length < 10) {
      throw new Error(`Invalid database ID for ${CITY}: "${DB_ID}". Please check NOTION_DATABASE_ID_${CITY.toUpperCase()} in GitHub Secrets.`);
    }
    
    const raw = await fetchAllPages();
    console.log(`✅ Raw pages fetched: ${raw.length}`);
    
    const mapped = raw.map(parseNotionPage);
    console.log(`✅ Pages mapped: ${mapped.length}`);
    
    // Leggi il contatore totale dei post scartati
    const totalRejectedCount = await getTotalRejectedCount();
    console.log(`📊 Total rejected posts by AI: ${totalRejectedCount}`);

    const outDir = path.join(process.cwd(), "public");
    if (!existsSync(outDir)) {
      console.log(`📁 Creating directory: ${outDir}`);
      await mkdir(outDir, { recursive: true });
    }

    const outPath = path.join(outDir, `data_${CITY}.json`);
    const payload = {
      generatedAt: new Date().toISOString(),
      city: CITY,
      count: mapped.length,
      totalRejectedCount: totalRejectedCount,
      results: mapped
    };

    console.log(`💾 Writing to: ${outPath}`);
    console.log(`📊 Payload: ${mapped.length} results, ${totalRejectedCount} rejected`);
    
    await writeFile(outPath, JSON.stringify(payload, null, 2), "utf-8");
    console.log(`✅ Successfully wrote ${outPath} with ${mapped.length} records (${totalRejectedCount} rejected by AI) for ${CITY}`);
    
  } catch (error) {
    console.error(`❌ Error in main():`, error);
    console.error(`❌ Stack trace:`, error.stack);
    
    // Non creare un file vuoto se il fetch fallisce
    console.error(`❌ Fetch failed for ${CITY}. Not creating empty data file.`);
    console.error(`❌ Please check:`);
    console.error(`   - Database ID: ${DB_ID}`);
    console.error(`   - API Key permissions`);
    console.error(`   - Database sharing settings`);
    
    process.exit(1);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
