import os, json, ssl, urllib.request

T = os.environ.get('CLOUDFLARE_API_TOKEN','')
A = 'edb167b78c9fb901ea5bca3ce58ccc4b'
ctx = ssl.create_default_context()
DB = '35e2e573-92f3-46ac-83c6-22f6429fc5e5'

def query(sql):
    b = json.dumps({'sql': sql, 'params': []}).encode()
    r = urllib.request.Request(
        f'https://api.cloudflare.com/client/v4/accounts/{A}/d1/database/{DB}/query',
        method='POST'
    )
    r.add_header('Authorization', f'Bearer {T}')
    r.add_header('Content-Type', 'application/json')
    r.data = b
    d = json.loads(urllib.request.urlopen(r, timeout=15, context=ctx).read())
    return d.get('result',[{}])[0].get('results',[])

print("=== PAPER CONTENT AUDIT ===")
for label, sql in [
    ('Total papers', 'SELECT COUNT(*) as c FROM papers'),
    ('With body_md (>100 chars)', "SELECT COUNT(*) as c FROM papers WHERE body_md IS NOT NULL AND length(body_md) > 100"),
    ('With DOI', "SELECT COUNT(*) as c FROM papers WHERE doi IS NOT NULL AND length(doi) > 5"),
    ('With R2 key', "SELECT COUNT(*) as c FROM papers WHERE r2_key IS NOT NULL AND length(r2_key) > 3"),
    ('METADATA-ONLY SHELLS', "SELECT COUNT(*) as c FROM papers WHERE (body_md IS NULL OR length(body_md) < 100) AND (doi IS NULL OR length(doi) < 5)"),
]:
    r = query(sql)
    print(f"  {label}: {r[0]['c'] if r else '?'}")

print()
print("=== SAMPLE SHELLS ===")
r = query("SELECT id, title, slug, source, created_at FROM papers WHERE (body_md IS NULL OR length(body_md) < 100) AND (doi IS NULL OR length(doi) < 5) ORDER BY created_at DESC LIMIT 8")
for row in r:
    title = str(row.get('title','?'))[:65]
    print(f"  id={row['id']} | slug={row.get('slug','?')[:30]} | src={row.get('source','?')[:15]} | {title}")
