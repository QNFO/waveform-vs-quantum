// r2-gateway Worker v1.0
// Centralized R2 write gateway for QNFO 6-bucket fleet
// Deployed at: r2-gateway.q08.workers.dev
// Canonical doc: R2-MULTI-BUCKET-ARCHITECTURE.md

const ACCOUNT_ID = 'edb167b78c9fb901ea5bca3ce58ccc4b';
const API_TOKEN = ''; // Set in wrangler secret: npx wrangler secret put API_TOKEN

const BUCKET_ROUTES = {
  'papers/': 'qnfo-releases',
  'releases/': 'qnfo-releases',
  'prompts/skills/': 'qnfo-skills',
  'tools/': 'qnfo-skills',
  'audit/': 'qnfo-audit',
  'kaizen/': 'qnfo-audit',
  'projects/': 'qnfo-projects',
  'backups/': 'qnfo-backups',
  'css/': 'qnfo-assets',
  'js/': 'qnfo-assets',
  'fonts/': 'qnfo-assets',
  'images/': 'qnfo-assets',
  'design-system/': 'qnfo-assets',
  'assets/': 'qnfo-assets',
  'discovery/': 'qnfo-audit',
};

const BANNED_PREFIXES = ['qnfo/', 'qnfo-', 'qwav/', 'deepchat/'];

function validateR2Key(key) {
  if (!key || typeof key !== 'string' || key.trim().length === 0)
    return { valid: false, error: 'Key must be a non-empty string' };
  if (key.includes('//'))
    return { valid: false, error: 'Key contains double slash' };
  for (const banned of BANNED_PREFIXES)
    if (key.startsWith(banned))
      return { valid: false, error: 'Banned prefix: ' + banned };
  return { valid: true };
}

function resolveBucket(key) {
  for (const [prefix, bucket] of Object.entries(BUCKET_ROUTES))
    if (key.startsWith(prefix)) return bucket;
  return 'qnfo-audit';
}

function cors() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Session-Id'
  };
}

function j(data, status) {
  return new Response(JSON.stringify(data, null, 2), {
    status: status || 200,
    headers: { 'Content-Type': 'application/json', ...cors() }
  });
}

async function lock(sid, rt, rid, ttl) {
  try {
    const r = await fetch('https://infra-lock-manager.q08.workers.dev/api/lock', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resourceType: rt, resourceId: rid, sessionId: sid, ttlSeconds: ttl || 60 })
    });
    return await r.json();
  } catch(e) { return { success: false, message: e.message }; }
}

async function unlock(sid, rt, rid) {
  try { await fetch('https://infra-lock-manager.q08.workers.dev/api/unlock', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resourceType: rt, resourceId: rid, sessionId: sid })
  }); } catch(_) {}
}

async function r2put(bucket, key, body, ct) {
  const u = 'https://api.cloudflare.com/client/v4/accounts/' + ACCOUNT_ID + '/r2/buckets/' + bucket + '/objects/' + encodeURIComponent(key);
  const r = await fetch(u, {
    method: 'PUT',
    headers: { 'Authorization': 'Bearer ' + API_TOKEN, 'Content-Type': ct || 'application/octet-stream' },
    body
  });
  return await r.json();
}

async function r2get(bucket, key) {
  const u = 'https://api.cloudflare.com/client/v4/accounts/' + ACCOUNT_ID + '/r2/buckets/' + bucket + '/objects/' + encodeURIComponent(key);
  const r = await fetch(u, { headers: { 'Authorization': 'Bearer ' + API_TOKEN } });
  return r.ok ? await r.arrayBuffer() : null;
}

export default {
  async fetch(request, env) {
    const u = new URL(request.url);
    const p = u.pathname;
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors() });

    if (p === '/health') return j({ status: 'ok', worker: 'r2-gateway', version: '1.0.0', buckets: [...new Set(Object.values(BUCKET_ROUTES))].length, routes: Object.keys(BUCKET_ROUTES).length });

    if (p === '/routes') return j({ buckets: [...new Set(Object.values(BUCKET_ROUTES))].sort(), routes: BUCKET_ROUTES, banned: BANNED_PREFIXES });

    if (p === '/resolve' && request.method === 'POST') {
      const { key } = await request.json().catch(() => ({}));
      const v = validateR2Key(key);
      if (!v.valid) return j(v, 400);
      return j({ key, bucket: resolveBucket(key), valid: true });
    }

    if (p === '/write' && request.method === 'POST') {
      const sid = request.headers.get('X-Session-Id') || 'r2-gateway';
      const { key, content, contentType } = await request.json().catch(() => ({}));
      if (!key) return j({ error: 'Missing: key' }, 400);

      const v = validateR2Key(key);
      if (!v.valid) return j(v, 400);

      const bucket = resolveBucket(key);
      const rid = bucket + '/' + key;
      const lk = await lock(sid, 'r2_object', rid, 60);
      if (!lk.success) return j({ status: 'blocked', reason: lk.message, key, bucket }, 409);

      try {
        const buf = typeof content === 'string' ? new TextEncoder().encode(content) : new Uint8Array(content || []);
        const pr = await r2put(bucket, key, buf, contentType);
        if (!pr.success) return j({ status: 'error', phase: 'write', error: pr.errors }, 500);

        const vbuf = await r2get(bucket, key);
        const verified = vbuf !== null && vbuf.byteLength === buf.byteLength;

        return j({ status: 'written', key, bucket, sizeBytes: buf.byteLength, verified, sessionId: sid, timestamp: new Date().toISOString() });
      } finally { await unlock(sid, 'r2_object', rid); }
    }

    return j({ worker: 'r2-gateway', endpoints: ['/health', '/routes', '/resolve', '/write'] });
  }
};
