/**
 * search-worker v1.2 — JavaScript rewrite
 * Semantic paper search via Vectorize + audit trail search
 * 
 * Bindings: DB (D1 qnfo-audit), VECTORIZE (Vectorize → qwav-research-v2), AI (Workers AI)
 */
const EMBEDDING_MODEL = "@cf/baai/bge-base-en-v1.5";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS, POST",
  "Access-Control-Allow-Headers": "Content-Type",
};

const SOURCE_URL_MAP = {
  "ultrametric-quantum": "https://quantum.qnfo.org",
  "quantum-laws-of-form": "https://laws.qnfo.org",
  "unity-of-ultrametric-physics": "https://unity.qnfo.org",
  "adelic-qft": "https://adelic.qnfo.org",
  "hierarchical-universe": "https://hierarchy.qnfo.org",
  "different-physics": "https://different.qnfo.org",
  "ultrametric-paradigm": "https://paradigm.qnfo.org",
  "ultrametric-ai-poc": "https://ai-poc.qnfo.org",
  "solo-scientist": "https://solo.qnfo.org",
  "cocyle": "https://cocyle.qnfo.org",
};

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...CORS_HEADERS },
  });
}

function htmlResponse(html, status = 200) {
  return new Response(html, {
    status,
    headers: { "Content-Type": "text/html; charset=utf-8", ...CORS_HEADERS },
  });
}

function parseQueryParams(url) {
  const params = {};
  const searchParams = new URL(url).searchParams;
  for (const key of ["q", "type", "limit", "thread_id"]) {
    const val = searchParams.get(key);
    if (val) params[key] = val;
  }
  return params;
}

async function generateEmbedding(env, text) {
  const result = await env.AI.run(EMBEDDING_MODEL, { text });
  if (Array.isArray(result)) return result[0];
  if (result?.data) return result.data[0];
  return null;
}

async function searchFts(db, query, searchType, limit) {
  limit = Math.min(limit, 50);
  const results = { events: [], tasks: [], wiki: [] };

  try {
    if (searchType === "events" || searchType === "all") {
      const r = await db.prepare(
        "SELECT e.* FROM events_fts f JOIN events e ON e.rowid = f.rowid WHERE events_fts MATCH ? ORDER BY rank LIMIT ?"
      ).bind(query, limit).all();
      results.events = r.results;
    }
  } catch {}
  try {
    if (searchType === "tasks" || searchType === "all") {
      const r = await db.prepare(
        "SELECT t.* FROM tasks_fts f JOIN tasks t ON t.rowid = f.rowid WHERE tasks_fts MATCH ? ORDER BY rank LIMIT ?"
      ).bind(query, limit).all();
      results.tasks = r.results;
    }
  } catch {}
  try {
    if (searchType === "wiki" || searchType === "all") {
      const r = await db.prepare(
        "SELECT w.* FROM wiki_fts f JOIN wiki_pages w ON w.rowid = f.rowid WHERE wiki_fts MATCH ? ORDER BY rank LIMIT ?"
      ).bind(query, limit).all();
      results.wiki = r.results;
    }
  } catch {}
  return results;
}

async function searchSemantic(env, query, limit) {
  limit = Math.min(limit, 20);
  const queryVector = await generateEmbedding(env, query);
  if (!queryVector) return { error: "Embedding generation failed" };

  try {
    const results = await env.VECTORIZE.query(queryVector, {
      topK: limit,
      returnValues: false,
      returnMetadata: true,
    });
    const matches = results.matches.map(m => ({
      id: String(m.id),
      score: m.score || 0,
      metadata: m.metadata || {},
    }));
    return { count: matches.length, matches };
  } catch (e) {
    return { error: String(e) };
  }
}

async function searchPapers(env, query, limit) {
  limit = Math.min(limit, 20);
  const queryVector = await generateEmbedding(env, query);
  if (!queryVector) return { error: "Embedding generation failed" };

  try {
    const results = await env.VECTORIZE.query(queryVector, {
      topK: limit,
      returnValues: false,
      returnMetadata: true,
    });
    const papers = results.matches.map(m => {
      const meta = m.metadata || {};
      let bestTitle = meta.title || meta.slug || "";
      if (!bestTitle) {
        const source = meta.source || "";
        const fname = meta.file || "";
        if (source && fname) bestTitle = `${source}/${fname}`;
        else if (source) bestTitle = source;
        else if (fname) bestTitle = fname;
        else bestTitle = "Untitled";
      }
      return {
        id: String(m.id),
        score: Math.round((m.score || 0) * 10000) / 10000,
        title: bestTitle,
        url: meta.url || SOURCE_URL_MAP[meta.source] || "",
        slug: meta.slug || "",
        source: meta.source || "",
        chunk: meta.chunk || null,
      };
    });
    return { query, count: papers.length, papers };
  } catch (e) {
    return { error: String(e) };
  }
}

async function searchCrossThread(db, threadId, limit) {
  limit = Math.min(limit, 50);
  const result = await db.prepare(
    "SELECT DISTINCT project, action FROM events WHERE thread_id = ? LIMIT 20"
  ).bind(threadId).all();

  const projects = new Set();
  const actions = new Set();
  for (const row of result.results) {
    if (row.project) projects.add(row.project);
    actions.add(row.action);
  }
  if (!projects.size && !actions.size) {
    return { thread_id: threadId, related: [], note: "No project/action data" };
  }

  const related = [];
  const seenIds = new Set();
  for (const proj of [...projects].slice(0, 5)) {
    const r = await db.prepare(
      "SELECT * FROM events WHERE project = ? AND thread_id != ? ORDER BY timestamp DESC LIMIT ?"
    ).bind(proj, threadId, limit).all();
    for (const row of r.results) {
      if (!seenIds.has(row.id)) {
        seenIds.add(row.id);
        related.push({ id: row.id, thread_id: row.thread_id, agent: row.agent, action: row.action, project: row.project, summary: row.summary, timestamp: row.timestamp });
      }
    }
  }

  if (related.length < limit) {
    const remaining = limit - related.length;
    for (const act of [...actions].slice(0, 3)) {
      const r = await db.prepare(
        "SELECT * FROM events WHERE action = ? AND thread_id != ? ORDER BY timestamp DESC LIMIT ?"
      ).bind(act, threadId, remaining).all();
      for (const row of r.results) {
        if (!seenIds.has(row.id)) {
          seenIds.add(row.id);
          related.push({ id: row.id, thread_id: row.thread_id, agent: row.agent, action: row.action, project: row.project, summary: row.summary, timestamp: row.timestamp });
        }
      }
    }
  }
  return { thread_id: threadId, count: related.length, related };
}

const API_DOCS = `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>QWAV Search API v1.2</title>
<style>body{font-family:system-ui;max-width:800px;margin:2rem auto;padding:0 1rem}
code{background:#f0f0f0;padding:.15em .4em;border-radius:3px}pre{background:#1a1a2e;color:#e0e0e0;padding:1rem;border-radius:6px}
.endpoint{background:#f8f8f8;padding:1rem;border-radius:6px;margin:1rem 0;border-left:4px solid #4a90d9}
.method{font-weight:bold;color:#4a90d9}</style></head><body>
<h1>QWAV Search API — search-worker v1.2 (JS)</h1>
<div class="endpoint"><p><span class="method">GET</span> <code>/api/search/papers?q=query&limit=10</code></p>
<p>Semantic paper search via Vectorize (bge-base-en-v1.5, 768-dim)</p></div>
<div class="endpoint"><p><span class="method">GET</span> <code>/api/search/semantic?q=query&limit=5</code></p>
<p>Raw semantic search across all Vectorize entries</p></div>
<div class="endpoint"><p><span class="method">GET</span> <code>/api/search?q=keyword&type=all&limit=10</code></p>
<p>FTS5 keyword search across events, tasks, wiki</p></div>
<div class="endpoint"><p><span class="method">GET</span> <code>/health</code></p><p>Health check</p></div>
</body></html>`;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    if (method === "OPTIONS") {
      return new Response("", { status: 204, headers: CORS_HEADERS });
    }

    if (path === "/" && method === "GET") {
      return htmlResponse(API_DOCS);
    }

    if (path === "/health" && method === "GET") {
      return jsonResponse({
        status: "ok",
        worker: "search-worker",
        version: "1.2",
        runtime: "javascript",
        embedding_model: EMBEDDING_MODEL,
        index: "qwav-research-v2",
      });
    }

    const params = parseQueryParams(request.url);

    if (path === "/api/search/papers") {
      if (method !== "GET") return jsonResponse({ error: "Only GET supported" }, 405);
      const query = params.q;
      if (!query) return jsonResponse({ error: "q parameter required" }, 400);
      const limit = Math.min(parseInt(params.limit) || 10, 20);
      return jsonResponse(await searchPapers(env, query, limit));
    }

    if (path === "/api/search") {
      if (method !== "GET") return jsonResponse({ error: "Only GET supported" }, 405);
      const query = params.q;
      if (!query) return jsonResponse({ error: "q parameter required" }, 400);
      const searchType = params.type || "all";
      const limit = Math.min(parseInt(params.limit) || 10, 50);
      const ftsResults = await searchFts(env.DB, query, searchType, limit);
      return jsonResponse({ query, type: searchType, method: "fts5", results: ftsResults });
    }

    if (path === "/api/search/semantic") {
      if (method !== "GET") return jsonResponse({ error: "Only GET supported" }, 405);
      const query = params.q;
      if (!query) return jsonResponse({ error: "q parameter required" }, 400);
      const limit = Math.min(parseInt(params.limit) || 5, 20);
      const results = await searchSemantic(env, query, limit);
      return jsonResponse({ query, method: "vectorize", results });
    }

    if (path === "/api/search/cross-thread") {
      if (method !== "GET") return jsonResponse({ error: "Only GET supported" }, 405);
      const threadId = params.thread_id;
      if (!threadId) return jsonResponse({ error: "thread_id required" }, 400);
      const limit = Math.min(parseInt(params.limit) || 20, 50);
      return jsonResponse(await searchCrossThread(env.DB, threadId, limit));
    }

    return jsonResponse({ error: "Not found", path }, 404);
  },
};
