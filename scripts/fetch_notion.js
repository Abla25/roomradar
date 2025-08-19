// scripts/fetch_notion.js
// Legge Notion con la chiave dai Secrets e scrive public/data.json

import { writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";

const NOTION_KEY = process.env.NOTION_API_KEY;
const DB_ID = process.env.NOTION_DATABASE_ID;

if (!NOTION_KEY || !DB_ID) {
  console.error("Mancano NOTION_API_KEY o NOTION_DATABASE_ID");
  process.exit(1);
}

async function fetchAllPages() {
  const results = [];
  let has_more = true;
  let next_cursor = undefined;

  while (has_more) {
    const body = {
      page_size: 100,
      ...(next_cursor ? { start_cursor: next_cursor } : {})
    };

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
      throw new Error(`Notion API ${r.status}: ${t}`);
    }

    const json = await r.json();
    results.push(...json.results);
    has_more = json.has_more;
    next_cursor = json.next_cursor;
  }
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
    title: get("Titolo_parafrasato", "title"),
    overview: get("Overview", "rich"),
    description: get("Descrizione_originale", "rich"),
    price: get("Prezzo", "rich"),
    zone: get("Zona", "rich"),
    zoneMacro: get("Zona_macro", "rich"),
    rooms: get("Camere", "rich"),
    reliability: get("Affidabilita", "number") || 0,
    reliabilityReason: get("Motivo_Rating", "rich"),
    datePublished: get("Data_Pubblicazione", "date"),
    dateAdded: get("Data_DB", "date"),
    link: get("Link", "url"),
    status: get("Status", "select"),
    imageUrl: get("Immagini", "url")
  };
}

async function main() {
  const raw = await fetchAllPages();
  const mapped = raw.map(parseNotionPage);

  const outDir = path.join(process.cwd(), "public");
  if (!existsSync(outDir)) await mkdir(outDir, { recursive: true });

  const outPath = path.join(outDir, "data.json");
  const payload = {
    generatedAt: new Date().toISOString(),
    count: mapped.length,
    results: mapped
  };

  await writeFile(outPath, JSON.stringify(payload, null, 2), "utf-8");
  console.log(`Scritto ${outPath} con ${mapped.length} record`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
