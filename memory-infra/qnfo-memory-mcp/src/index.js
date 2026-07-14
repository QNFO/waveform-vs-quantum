/**
 * qnfo-memory-mcp Worker v1.0
 * MCP Protocol server exposing QNFO memory, search, and graph tools.
 * 
 * MCP Transport: SSE (Server-Sent Events) with POST /mcp endpoint
 * Tools: search_papers, search_memories, remember_fact, recall_facts, query_graph, get_paper_context
 * 
 * External services called:
 *   - search-worker: Paper semantic search (Vectorize)
 *   - qnfo-ai-worker: Embeddings, summarization
 *   - graph-api: Knowledge graph queries
 *   - D1 qnfo-graph: agent_memories table for full content
 *   - Vectorize qnfo-handoffs: Memory context vector storage
 */

// === MCP Protocol Constants ===
const PROTOCOL_VERSION = "2024-11-05";
const SERVER_NAME = "qnfo-memory-mcp";
const SERVER_VERSION = "1.0.0";

// === External API endpoints ===
const SEARCH_WORKER = "https://search-worker.q08.workers.dev";
const AI_WORKER = "https://qnfo-ai-worker.q08.workers.dev";
const GRAPH_API = "https://graph-api.q08.workers.dev";
const D1_GRAPH_ID = "a1954b92-d681-4d02-b1f6-f9a2eb4c265d";
const ACCOUNT_ID = "edb167b78c9fb901ea5bca3ce58ccc4b";

// === Tool Definitions ===
const TOOLS = [
  {
    name: "search_papers",
    description: "Semantic search across QWAV research papers using Vectorize. Returns top-k papers ranked by meaning similarity, not keywords.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Natural language search query" },
        limit: { type: "number", description: "Maximum results (1-20, default 10)", default: 10 }
      },
      required: ["query"]
    }
  },
  {
    name: "search_memories",
    description: "Semantic search across persistent agent memories stored in Vectorize. Find past conversations, decisions, and facts by meaning.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Natural language query about past memories" },
        limit: { type: "number", description: "Maximum results (1-20, default 5)", default: 5 },
        category: { type: "string", description: "Optional memory category filter (user_preference, project_fact, task_outcome, heuristic, anti_pattern)" }
      },
      required: ["query"]
    }
  },
  {
    name: "remember_fact",
    description: "Store a durable fact or memory with vector embedding for future semantic recall. Content is stored in D1 and Vectorize.",
    inputSchema: {
      type: "object",
      properties: {
        content: { type: "string", description: "The fact or memory to store" },
        category: { type: "string", description: "Category: user_preference, project_fact, task_outcome, heuristic, anti_pattern", enum: ["user_preference", "project_fact", "task_outcome", "heuristic", "anti_pattern"] },
        importance: { type: "number", description: "Importance 0-1 (default 0.7)", default: 0.7 },
        summary: { type: "string", description: "Short summary for retrieval display" },
        session_id: { type: "string", description: "Session identifier" }
      },
      required: ["content", "category"]
    }
  },
  {
    name: "recall_facts",
    description: "Recall stored facts from D1 by category or keyword match. For semantic search, use search_memories.",
    inputSchema: {
      type: "object",
      properties: {
        category: { type: "string", description: "Memory category filter" },
        keyword: { type: "string", description: "Keyword to search in content" },
        limit: { type: "number", description: "Maximum results (default 10)", default: 10 }
      },
      required: []
    }
  },
  {
    name: "query_graph",
    description: "Query the QNFO Knowledge Graph (3,242 nodes, 4,697 edges). Supports stats, nodes by label, neighbors, impact analysis, and raw SQL.",
    inputSchema: {
      type: "object",
      properties: {
        endpoint: { type: "string", description: "Graph API endpoint: stats, nodes, neighbors/{id}, impact/{id}, query", enum: ["stats", "nodes", "neighbors", "impact", "query"] },
        params: { type: "object", description: "Endpoint-specific parameters (label, search, id, query, etc.)" }
      },
      required: ["endpoint"]
    }
  },
  {
    name: "get_paper_context",
    description: "Get full paper body content from D1 living-paper database by slug or paper ID.",
    inputSchema: {
      type: "object",
      properties: {
        slug: { type: "string", description: "Paper slug or identifier" },
        limit_chars: { type: "number", description: "Maximum characters to return (default 5000)", default: 5000 }
      },
      required: ["slug"]
    }
  }
];

// === CORS headers ===
function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, Mcp-Session-Id"
  };
}

// === JSON response helper ===
function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders() }
  });
}

// === SSE response helper ===
function sseResponse() {
  let closed = false;
  const { readable, writable } = new TransformStream();
  const writer = writable.getWriter();
  const encoder = new TextEncoder();

  function send(data) {
    if (closed) return;
    const text = `data: ${JSON.stringify(data)}\n\n`;
    writer.write(encoder.encode(text));
  }

  return {
    response: new Response(readable, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        ...corsHeaders()
      }
    }),
    send,
    close: () => {
      closed = true;
      writer.close();
    }
  };
}

// === Embedding helper — uses MCP Worker's own AI binding ===
// bge-base-en-v1.5 = 768-dim, matches qnfo-handoffs Vectorize index
const MEMORY_EMBED_MODEL = "@cf/baai/bge-base-en-v1.5";

async function getEmbedding(text, env) {
  try {
    const result = await env.AI.run(MEMORY_EMBED_MODEL, { text });
    if (Array.isArray(result)) return result[0];
    if (result?.data) return result.data[0];
    return null;
  } catch (e) {
    console.error("Embedding failed:", e.message);
    return null;
  }
}

// === TOOL: search_papers ===
async function tool_search_papers(args, env) {
  const query = args.query;
  if (!query) {
    return { content: [{ type: "text", text: "Missing required: query" }], isError: true };
  }
  const limit = Math.max(1, Math.min(args.limit || 10, 20));

  // Use MCP Worker's own AI binding for embedding (avoid subrequest CPU timeout)
  const embedding = await getEmbedding(query, env);
  if (!embedding) {
    return { content: [{ type: "text", text: "Failed to generate embedding for query" }], isError: true };
  }

  // Query qwav-research-v2 Vectorize index directly via binding
  try {
    const results = await env.PAPER_VZ.query(embedding, {
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
        url: meta.url || "",
        slug: meta.slug || "",
        source: meta.source || "",
        chunk: meta.chunk || null,
      };
    });

    return {
      content: [{
        type: "text",
        text: JSON.stringify({ query, count: papers.length, papers }, null, 2)
      }]
    };
  } catch (e) {
    return { content: [{ type: "text", text: `Paper search failed: ${e.message}` }], isError: true };
  }
}

// === TOOL: search_memories ===
async function tool_search_memories(args, env) {
  const query = args.query;
  const limit = Math.min(args.limit || 5, 20);
  const category = args.category || null;

  // Generate embedding for the query using Workers AI binding
  const embedding = await getEmbedding(query, env);
  if (!embedding) {
    return { content: [{ type: "text", text: "Failed to generate embedding for query" }], isError: true };
  }

  try {
    // Query Vectorize (qnfo-handoffs index — 768-dim) via direct binding
    const results = await env.MEMORY_VZ.query(embedding, {
      topK: limit,
      returnValues: false,
      returnMetadata: true,
    });
    
    const matches = results.matches
      .filter(m => !category || (m.metadata?.category === category))
      .map(m => ({
        id: String(m.id),
        score: Math.round((m.score || 0) * 10000) / 10000,
        category: m.metadata?.category || "unknown",
        summary: m.metadata?.summary || "No summary",
        session_id: m.metadata?.session_id,
        timestamp: m.metadata?.timestamp,
      }));

    return {
      content: [{
        type: "text",
        text: JSON.stringify({ query, count: matches.length, memories: matches }, null, 2)
      }]
    };
  } catch (e) {
    // Fallback to D1-based recall if Vectorize query fails
    return await tool_recall_facts({ keyword: query, limit, category }, env);
  }
}

// === TOOL: remember_fact ===
async function tool_remember_fact(args, env) {
  const { content, category, importance = 0.7, summary, session_id } = args;
  
  // Input validation (RED-TEAM C2 fix)
  if (!content || !category) {
    const missing = [];
    if (!content) missing.push("content");
    if (!category) missing.push("category");
    return { content: [{ type: "text", text: `Missing required: ${missing.join(", ")}` }], isError: true };
  }
  const id = `mem:${category}:${Date.now()}:${crypto.randomUUID().slice(0, 8)}`;
  const memSummary = summary || content.slice(0, 200);
  const timestamp = new Date().toISOString();

  let d1Ok = false;
  let vzOk = false;

  // 1. Store in D1 via direct binding
  try {
    await env.MEMORY_DB.prepare(
      "INSERT INTO agent_memories (id, category, content, summary, importance, session_id, metadata_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    ).bind(id, category, content, memSummary, importance, session_id || null, JSON.stringify({ source: "qnfo-memory-mcp", timestamp }), timestamp).run();
    d1Ok = true;
  } catch (e) {
    console.error("D1 insert failed:", e.message);
  }

  // 2. Generate embedding via Workers AI binding (768-dim = matches qnfo-handoffs)
  const embedding = await getEmbedding(content, env);

  // 3. Upsert to Vectorize (qnfo-handoffs) via direct binding
  if (embedding) {
    try {
      await env.MEMORY_VZ.upsert([{
        id,
        values: embedding,
        metadata: {
          category,
          summary: memSummary,
          importance: String(importance),
          session_id: session_id || "unknown",
          timestamp,
        }
      }]);
      vzOk = true;
    } catch (e) {
      console.error("Vectorize upsert failed:", e.message);
    }
  }

  return {
    content: [{
      type: "text",
      text: JSON.stringify({
        status: "remembered",
        id,
        category,
        importance,
        summary: memSummary,
        storage: { d1: d1Ok, vectorize: vzOk },
        timestamp,
      }, null, 2)
    }]
  };
}

// === TOOL: recall_facts ===
async function tool_recall_facts(args, env) {
  const { category, keyword, limit = 10 } = args;
  
  let sql = "SELECT id, category, summary, importance, created_at, session_id FROM agent_memories WHERE 1=1";
  const params = [];

  if (category) {
    sql += " AND category = ?";
    params.push(category);
  }
  if (keyword) {
    sql += " AND (content LIKE ? OR summary LIKE ?)";
    params.push(`%${keyword}%`, `%${keyword}%`);
  }
  sql += " ORDER BY created_at DESC LIMIT ?";
  params.push(Math.max(1, Math.min(limit, 50)));

  try {
    const result = await env.MEMORY_DB.prepare(sql).bind(...params).all();
    const facts = (result.results || []).map(r => ({
      id: r.id,
      category: r.category,
      summary: r.summary,
      importance: r.importance,
      created_at: r.created_at,
      session_id: r.session_id,
    }));

    return {
      content: [{
        type: "text",
        text: JSON.stringify({ count: facts.length, facts }, null, 2)
      }]
    };
  } catch (e) {
    return { content: [{ type: "text", text: `D1 recall failed: ${e.message}` }], isError: true };
  }
}

// === TOOL: query_graph ===
async function tool_query_graph(args) {
  const { endpoint, params = {} } = args;
  let url = `${GRAPH_API}`;

  switch (endpoint) {
    case "stats":
      url += "/stats";
      break;
    case "nodes":
      url += `/nodes?label=${params.label || "Project"}&search=${params.search || ""}`;
      break;
    case "neighbors":
      url += `/neighbors/${encodeURIComponent(params.id || "")}`;
      break;
    case "impact":
      url += `/impact/${encodeURIComponent(params.id || "")}`;
      break;
    case "query":
      // POST /query with SQL
      try {
        const resp = await fetch(`${GRAPH_API}/query`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: params.query, params: params.params || [] })
        });
        const data = await resp.json();
        return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
      } catch (e) {
        return { content: [{ type: "text", text: `Graph query failed: ${e.message}` }], isError: true };
      }
    default:
      return { content: [{ type: "text", text: `Unknown endpoint: ${endpoint}` }], isError: true };
  }

  try {
    const resp = await fetch(url, { headers: { "User-Agent": "qnfo-memory-mcp/1.0" } });
    const data = await resp.json();
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  } catch (e) {
    return { content: [{ type: "text", text: `Graph API unreachable: ${e.message}` }], isError: true };
  }
}

// === TOOL: get_paper_context ===
async function tool_get_paper_context(args, env) {
  const slug = args.slug;
  if (!slug) {
    return { content: [{ type: "text", text: "Missing required: slug" }], isError: true };
  }
  const limit_chars = Math.max(100, args.limit_chars || 5000);
  const D1_LIVING_PAPER = "70a58cb3-b2cd-498d-877f-ecca86859a22";

  try {
    const d1Url = `https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/d1/database/${D1_LIVING_PAPER}/query`;
    
    // Try exact match first
    let resp = await fetch(d1Url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.CF_API_TOKEN}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        sql: "SELECT slug, title, body_md, created_at FROM papers WHERE slug = ? LIMIT 1",
        params: [slug]
      })
    });
    let data = await resp.json();
    let paper = data.result?.[0]?.results?.[0];

    if (!paper) {
      // Try partial match
      resp = await fetch(d1Url, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${env.CF_API_TOKEN}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          sql: "SELECT slug, title, body_md, created_at FROM papers WHERE slug LIKE ? LIMIT 1",
          params: [`%${slug}%`]
        })
      });
      data = await resp.json();
      paper = data.result?.[0]?.results?.[0];
    }

    if (!paper) {
      return { content: [{ type: "text", text: `Paper "${slug}" not found in living-paper D1` }], isError: true };
    }

    const body = (paper.body_md || "").slice(0, limit_chars);
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          slug: paper.slug,
          title: paper.title,
          body_preview: body,
          truncated: (paper.body_md || "").length > limit_chars,
          created_at: paper.created_at
        }, null, 2)
      }]
    };
  } catch (e) {
    return { content: [{ type: "text", text: `Paper lookup failed: ${e.message}` }], isError: true };
  }
}

// === Tool dispatcher ===
async function callTool(name, args, env) {
  switch (name) {
    case "search_papers": return await tool_search_papers(args, env);
    case "search_memories": return await tool_search_memories(args, env);
    case "remember_fact": return await tool_remember_fact(args, env);
    case "recall_facts": return await tool_recall_facts(args, env);
    case "query_graph": return await tool_query_graph(args);
    case "get_paper_context": return await tool_get_paper_context(args, env);
    default:
      return { content: [{ type: "text", text: `Unknown tool: ${name}` }], isError: true };
  }
}

// === Main fetch handler ===
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    // Health check
    if (url.pathname === "/health") {
      return json({
        status: "ok",
        server: SERVER_NAME,
        version: SERVER_VERSION,
        protocol: PROTOCOL_VERSION,
        tools: TOOLS.map(t => t.name),
        endpoints: {
          mcp_sse: "/mcp/sse",
          mcp_post: "/mcp"
        }
      });
    }

    // === MCP SSE Endpoint (GET /mcp/sse) ===
    if (url.pathname === "/mcp/sse" && request.method === "GET") {
      const sse = sseResponse();
      
      // Send endpoint event for Streamable HTTP
      sse.send({
        jsonrpc: "2.0",
        method: "endpoint",
        params: { uri: `${url.origin}/mcp` }
      });

      // Keep alive briefly then close (stateless MCP)
      setTimeout(() => sse.close(), 100);
      
      return sse.response;
    }

    // === MCP POST Endpoint ===
    if (url.pathname === "/mcp" && request.method === "POST") {
      let body;
      try {
        body = await request.json();
      } catch {
        return json({ jsonrpc: "2.0", error: { code: -32700, message: "Parse error" }, id: null }, 400);
      }

      const { method, params, id } = body;

      // Initialize
      if (method === "initialize") {
        return json({
          jsonrpc: "2.0",
          id,
          result: {
            protocolVersion: PROTOCOL_VERSION,
            capabilities: { tools: {} },
            serverInfo: { name: SERVER_NAME, version: SERVER_VERSION }
          }
        });
      }

      // Initialized notification (no response needed)
      if (method === "notifications/initialized") {
        return new Response(null, { status: 200, headers: corsHeaders() });
      }

      // List tools
      if (method === "tools/list") {
        return json({
          jsonrpc: "2.0",
          id,
          result: { tools: TOOLS }
        });
      }

      // Call tool
      if (method === "tools/call") {
        const toolResult = await callTool(params.name, params.arguments || {}, env);
        return json({
          jsonrpc: "2.0",
          id,
          result: toolResult
        });
      }

      // List resources (empty — no resources exposed)
      if (method === "resources/list") {
        return json({ jsonrpc: "2.0", id, result: { resources: [] } });
      }

      // Unknown method
      return json({
        jsonrpc: "2.0",
        id: id || null,
        error: { code: -32601, message: `Method not found: ${method}` }
      });
    }

    // Fallback
    return json({ error: "Not found", path: url.pathname }, 404);
  }
};
