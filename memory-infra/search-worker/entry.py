"""search-worker v1.2 — Semantic paper search via Vectorize + audit trail search
Fixed: dimension mismatch resolved, binding refresh, bge-base-en-v1.5 (768-dim)

Bindings: DB (D1 qnfo-audit), VECTORIZE (Vectorize → qwav-research-v2), AI (Workers AI)
API:
  GET / — API docs (HTML)
  GET /api/search?q=keyword&type=events|tasks|wiki|all&limit=10
  GET /api/search/semantic?q=natural+language+query&limit=5
  GET /api/search/papers?q=natural+language+query&limit=10
  GET /api/search/cross-thread?thread_id=XXX
  GET /health — Health check
"""
from js import Response, URL
import json as _json

# Use plain Python dicts — no JS Object.fromEntries at module level (breaks Python Workers snapshot)
_CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS, POST",
    "Access-Control-Allow-Headers": "Content-Type",
}

EMBEDDING_MODEL = "@cf/baai/bge-base-en-v1.5"

SOURCE_URL_MAP = {
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
}


def _make_headers(extra=None):
    """Build JS Headers object from Python dict."""
    h = dict(_CORS)
    if extra:
        h.update(extra)
    return h


def json_response(data, status=200):
    body = _json.dumps(data)
    return Response.new(body, {"status": status, "headers": _make_headers({"Content-Type": "application/json"})})


def html_response(html, status=200):
    return Response.new(html, {"status": status, "headers": _make_headers({"Content-Type": "text/html; charset=utf-8"})})


def parse_query_params(url):
    params = {}
    search = URL.new(url).searchParams
    for key in ["q", "type", "limit", "thread_id"]:
        val = search.get(key)
        if val:
            params[key] = val
    return params


async def generate_embedding(env, text):
    """Generate embedding using Workers AI bge-base-en-v1.5 (768-dim)."""
    embed_result = await env.AI.run(
        EMBEDDING_MODEL,
        Object.fromEntries([["text", text]])
    )
    if isinstance(embed_result, list):
        return embed_result[0]
    elif hasattr(embed_result, 'data'):
        return embed_result.data[0]
    return None


async def search_fts(db, query, search_type, limit):
    """Keyword search using D1 FTS5."""
    limit = min(limit, 50)
    results = {"events": [], "tasks": [], "wiki": []}
    try:
        r = await db.prepare(
            "SELECT e.* FROM events_fts f JOIN events e ON e.rowid = f.rowid "
            "WHERE events_fts MATCH ? ORDER BY rank LIMIT ?"
        ).bind(query, limit).all()
        for row in r.results:
            results["events"].append(dict(row))
    except: pass
    try:
        r = await db.prepare(
            "SELECT t.* FROM tasks_fts f JOIN tasks t ON t.rowid = f.rowid "
            "WHERE tasks_fts MATCH ? ORDER BY rank LIMIT ?"
        ).bind(query, limit).all()
        for row in r.results:
            results["tasks"].append(dict(row))
    except: pass
    try:
        r = await db.prepare(
            "SELECT w.* FROM wiki_fts f JOIN wiki_pages w ON w.rowid = f.rowid "
            "WHERE wiki_fts MATCH ? ORDER BY rank LIMIT ?"
        ).bind(query, limit).all()
        for row in r.results:
            results["wiki"].append(dict(row))
    except: pass
    return results


async def search_semantic(env, query, limit):
    """Semantic search using Vectorize with AI-embedded query."""
    limit = min(limit, 20)
    query_vector = await generate_embedding(env, query)
    if query_vector is None:
        return {"error": "Embedding generation failed"}
    try:
        results = await env.VECTORIZE.query(query_vector, Object.fromEntries([
            ["topK", limit],
            ["returnValues", False],
            ["returnMetadata", True],
        ]))
        matches = []
        for m in results.matches:
            meta = {}
            if m.metadata:
                try:
                    meta = dict(Object.entries(m.metadata))
                except:
                    try:
                        meta = dict(m.metadata)
                    except:
                        pass
            match = {"id": str(m.id), "score": float(m.score) if hasattr(m, 'score') else 0.0, "metadata": meta}
            matches.append(match)
        return {"count": len(matches), "matches": matches}
    except Exception as e:
        return {"error": str(e)}


async def search_papers(env, query, limit):
    """Search papers in qwav-research-v2 Vectorize index."""
    limit = min(limit, 20)
    query_vector = await generate_embedding(env, query)
    if query_vector is None:
        return {"error": "Embedding generation failed"}
    try:
        results = await env.VECTORIZE.query(query_vector, Object.fromEntries([
            ["topK", limit],
            ["returnValues", False],
            ["returnMetadata", True],
        ]))
        papers = []
        for m in results.matches:
            meta = {}
            if m.metadata:
                try:
                    meta = dict(Object.entries(m.metadata))
                except:
                    try:
                        meta = dict(m.metadata)
                    except:
                        pass
            best_title = meta.get("title", "") or meta.get("slug", "")
            if not best_title:
                source = meta.get("source", "")
                fname = meta.get("file", "")
                if source and fname:
                    best_title = f"{source}/{fname}"
                elif source:
                    best_title = source
                elif fname:
                    best_title = fname
                else:
                    best_title = "Untitled"
            papers.append({
                "id": str(m.id),
                "score": round(float(m.score), 4) if hasattr(m, 'score') else 0.0,
                "title": best_title,
                "url": meta.get("url", "") or SOURCE_URL_MAP.get(meta.get("source", ""), ""),
                "slug": meta.get("slug", ""),
                "source": meta.get("source", ""),
                "chunk": meta.get("chunk", None),
            })
        return {"query": query, "count": len(papers), "papers": papers}
    except Exception as e:
        return {"error": str(e)}


async def search_cross_thread(db, thread_id, limit):
    """Find events from OTHER threads that may be related."""
    limit = min(limit, 50)
    result = await db.prepare(
        "SELECT DISTINCT project, action FROM events WHERE thread_id = ? LIMIT 20"
    ).bind(thread_id).all()
    projects, actions = set(), set()
    for row in result.results:
        if row.project: projects.add(row.project)
        actions.add(row.action)
    if not projects and not actions:
        return {"thread_id": thread_id, "related": [], "note": "No project/action data"}
    related, seen_ids = [], set()
    for proj in list(projects)[:5]:
        r = await db.prepare(
            "SELECT * FROM events WHERE project = ? AND thread_id != ? ORDER BY timestamp DESC LIMIT ?"
        ).bind(proj, thread_id, limit).all()
        for row in r.results:
            if row.id not in seen_ids:
                seen_ids.add(row.id)
                related.append({"id": row.id, "thread_id": row.thread_id, "agent": row.agent, "action": row.action, "project": row.project, "summary": row.summary, "timestamp": row.timestamp})
    if len(related) < limit:
        remaining = limit - len(related)
        for act in list(actions)[:3]:
            r = await db.prepare(
                "SELECT * FROM events WHERE action = ? AND thread_id != ? ORDER BY timestamp DESC LIMIT ?"
            ).bind(act, thread_id, remaining).all()
            for row in r.results:
                if row.id not in seen_ids:
                    seen_ids.add(row.id)
                    related.append({"id": row.id, "thread_id": row.thread_id, "agent": row.agent, "action": row.action, "project": row.project, "summary": row.summary, "timestamp": row.timestamp})
    return {"thread_id": thread_id, "count": len(related), "related": related}


API_DOCS = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>QWAV Search API v1.2</title>
<style>body{font-family:system-ui;max-width:800px;margin:2rem auto;padding:0 1rem}
code{background:#f0f0f0;padding:.15em .4em;border-radius:3px}
pre{background:#1a1a2e;color:#e0e0e0;padding:1rem;border-radius:6px}
.endpoint{background:#f8f8f8;padding:1rem;border-radius:6px;margin:1rem 0;border-left:4px solid #4a90d9}
.method{font-weight:bold;color:#4a90d9}</style></head><body>
<h1>QWAV Search API — search-worker v1.2</h1>
<div class="endpoint"><p><span class="method">GET</span> <code>/api/search/papers?q=query&limit=10</code></p>
<p>Semantic paper search via Vectorize (bge-base-en-v1.5, 768-dim)</p></div>
<div class="endpoint"><p><span class="method">GET</span> <code>/api/search/semantic?q=query&limit=5</code></p>
<p>Raw semantic search across all Vectorize entries</p></div>
<div class="endpoint"><p><span class="method">GET</span> <code>/api/search?q=keyword&type=all&limit=10</code></p>
<p>FTS5 keyword search across events, tasks, wiki</p></div>
<div class="endpoint"><p><span class="method">GET</span> <code>/health</code></p><p>Health check</p></div>
</body></html>"""


async def fetch(request, env):
    url_obj = URL.new(request.url)
    path = url_obj.pathname
    method = request.method

    if method == "OPTIONS":
        return Response.new("", {"status": 204, "headers": _make_headers()})

    if path == "/" and method == "GET":
        return html_response(API_DOCS)

    if path == "/health" and method == "GET":
        return json_response({"status": "ok", "worker": "search-worker", "version": "1.2", "embedding_model": EMBEDDING_MODEL, "index": "qwav-research-v2"})

    params = parse_query_params(request.url)

    if path == "/api/search/papers":
        if method != "GET":
            return json_response({"error": "Only GET supported"}, 405)
        query = params.get("q", "")
        if not query:
            return json_response({"error": "q parameter required"}, 400)
        try:
            limit = min(int(params.get("limit", 10)), 20)
        except:
            return json_response({"error": "limit must be a number"}, 400)
        results = await search_papers(env, query, limit)
        return json_response(results)

    if path == "/api/search":
        if method != "GET":
            return json_response({"error": "Only GET supported"}, 405)
        query = params.get("q", "")
        if not query:
            return json_response({"error": "q parameter required"}, 400)
        search_type = params.get("type", "all")
        try:
            limit = min(int(params.get("limit", 10)), 50)
        except:
            return json_response({"error": "limit must be a number"}, 400)
        fts_results = await search_fts(env.DB, query, search_type, limit)
        return json_response({"query": query, "type": search_type, "method": "fts5", "results": fts_results})

    if path == "/api/search/semantic":
        if method != "GET":
            return json_response({"error": "Only GET supported"}, 405)
        query = params.get("q", "")
        if not query:
            return json_response({"error": "q parameter required"}, 400)
        try:
            limit = min(int(params.get("limit", 5)), 20)
        except:
            return json_response({"error": "limit must be a number"}, 400)
        results = await search_semantic(env, query, limit)
        return json_response({"query": query, "method": "vectorize", "results": results})

    if path == "/api/search/cross-thread":
        if method != "GET":
            return json_response({"error": "Only GET supported"}, 405)
        thread_id = params.get("thread_id", "")
        if not thread_id:
            return json_response({"error": "thread_id required"}, 400)
        try:
            limit = min(int(params.get("limit", 20)), 50)
        except:
            return json_response({"error": "limit must be a number"}, 400)
        return json_response(await search_cross_thread(env.DB, thread_id, limit))

    return json_response({"error": "Not found", "path": path}, 404)
