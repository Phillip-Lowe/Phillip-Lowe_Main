const http = require('http');
const Database = require('better-sqlite3');
const path = require('path');

const DB_PATH = '/Users/philliplowe/.openclaw/workspaces/sol/green-systems-crm.db';
const PORT = 3456;

const db = new Database(DB_PATH);

// Helper: parse JSON body
function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', chunk => data += chunk);
    req.on('end', () => {
      try {
        resolve(JSON.parse(data));
      } catch (e) {
        reject(new Error('Invalid JSON'));
      }
    });
    req.on('error', reject);
  });
}

// Upsert statement (matches n8n Code node query)
const upsert = db.prepare(`
  INSERT INTO leads (
    place_id, name, address, phone, website, rating, review_count,
    category, score, stage, owner, created_date, source,
    has_order_online, has_doordash, has_ubereats, has_grubhub,
    has_square, has_toast, has_chownow, email, last_scraped
  ) VALUES (
    @place_id, @name, @address, @phone, @website, @rating, @review_count,
    @category, @score, @stage, @owner, @created_date, @source,
    @has_order_online, @has_doordash, @has_ubereats, @has_grubhub,
    @has_square, @has_toast, @has_chownow, @email, @last_scraped
  )
  ON CONFLICT(place_id) DO UPDATE SET
    name = excluded.name,
    address = excluded.address,
    phone = excluded.phone,
    website = excluded.website,
    rating = excluded.rating,
    review_count = excluded.review_count,
    category = excluded.category,
    score = excluded.score,
    stage = excluded.stage,
    owner = excluded.owner,
    created_date = excluded.created_date,
    source = excluded.source,
    has_order_online = excluded.has_order_online,
    has_doordash = excluded.has_doordash,
    has_ubereats = excluded.has_ubereats,
    has_grubhub = excluded.has_grubhub,
    has_square = excluded.has_square,
    has_toast = excluded.has_toast,
    has_chownow = excluded.has_chownow,
    email = excluded.email,
    last_scraped = excluded.last_scraped
`);

const server = http.createServer(async (req, res) => {
  const url = req.url;
  const method = req.method;

  res.setHeader('Content-Type', 'application/json');

  if (url === '/health' && method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({ status: 'ok' }));
    return;
  }

  if (url === '/leads' && method === 'POST') {
    try {
      const body = await readBody(req);
      const params = {
        place_id: body.place_id ?? null,
        name: body.name ?? null,
        address: body.address ?? null,
        phone: body.phone ?? null,
        website: body.website ?? null,
        rating: body.rating ?? null,
        review_count: body.review_count ?? null,
        category: body.category ?? null,
        score: body.score ?? null,
        stage: body.stage ?? 'New',
        owner: body.owner ?? 'Green',
        created_date: body.created_date ?? null,
        source: body.source ?? null,
        has_order_online: body.has_order_online ?? 0,
        has_doordash: body.has_doordash ?? 0,
        has_ubereats: body.has_ubereats ?? 0,
        has_grubhub: body.has_grubhub ?? 0,
        has_square: body.has_square ?? 0,
        has_toast: body.has_toast ?? 0,
        has_chownow: body.has_chownow ?? 0,
        email: body.email ?? null,
        last_scraped: body.last_scraped ?? new Date().toISOString()
      };

      if (!params.place_id) {
        res.writeHead(400);
        res.end(JSON.stringify({ success: false, error: 'place_id is required' }));
        return;
      }

      const result = upsert.run(params);
      console.log(`[${new Date().toISOString()}] Upserted lead ${params.place_id} — changes: ${result.changes}`);

      res.writeHead(200);
      res.end(JSON.stringify({ success: true, changes: result.changes }));
    } catch (err) {
      console.error(`[${new Date().toISOString()}] Error:`, err.message);
      res.writeHead(500);
      res.end(JSON.stringify({ success: false, error: err.message }));
    }
    return;
  }

  res.writeHead(404);
  res.end(JSON.stringify({ success: false, error: 'Not found' }));
});

server.listen(PORT, () => {
  console.log(`Systack Pipeline API running on http://localhost:${PORT}`);
});
