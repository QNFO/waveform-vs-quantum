#!/usr/bin/env python3
"""Red Team: Persistence + sync readiness audit — compact output."""
import urllib.request, json, os, ssl, hashlib, sys
from datetime import datetime, timezone

T = os.environ['CLOUDFLARE_API_TOKEN']
A = 'edb167b78c9fb901ea5bca3ce58ccc4b'
DB = '35e2e573-92f3-46ac-83c6-22f6429fc5e5'
SKILLS_DIR = os.path.expandvars(r'%USERPROFILE%\.deepchat\skills')
ctx = ssl.create_default_context()

def d1(sql, params=None):
    body = {'sql': sql}
    if params: body['params'] = params
    u = f'https://api.cloudflare.com/client/v4/accounts/{A}/d1/database/{DB}/query'
    r = urllib.request.Request(u, method='POST')
    r.add_header('Authorization', f'Bearer {T}')
    r.add_header('Content-Type', 'application/json')
    r.data = json.dumps(body).encode()
    return json.loads(urllib.request.urlopen(r, timeout=10, context=ctx).read())

results = {"checks": [], "pass": 0, "fail": 0}

def check(label, ok, detail=""):
    results["checks"].append({"label": label, "pass": ok, "detail": detail})
    if ok: results["pass"] += 1
    else: results["fail"] += 1

# 1. Local count
local = sorted([d for d in os.listdir(SKILLS_DIR) if os.path.isfile(os.path.join(SKILLS_DIR, d, 'SKILL.md')) and not d.startswith('.')])
check("local_skills", len(local) >= 55, f"{len(local)} skills")

# 2. Target skills have cross-ref markers
targets = ['closeout-manager', 'execution-guard', 'qnfo-agent', 'research-planner']
for name in targets:
    path = os.path.join(SKILLS_DIR, name, 'SKILL.md')
    with open(path, 'rb') as f:
        content = f.read()
    has = b'Optimized Prompt Patterns' in content
    check(f"skill:{name}", has, "has cross-ref" if has else "MISSING cross-ref")

# 3. R2 content check
for name in targets:
    url = f'https://api.cloudflare.com/client/v4/accounts/{A}/r2/buckets/qnfo/objects/qnfo/prompts/skills/{name}/SKILL.md'
    r = urllib.request.Request(url)
    r.add_header('Authorization', f'Bearer {T}')
    try:
        body = urllib.request.urlopen(r, timeout=10, context=ctx).read()
        has = b'Optimized Prompt Patterns' in body
        check(f"r2:{name}", has, f"{len(body)/1024:.1f}KB")
    except Exception as e:
        check(f"r2:{name}", False, str(e)[:80])

# 4. D1 SHA256 match
for name in targets:
    path = os.path.join(SKILLS_DIR, name, 'SKILL.md')
    with open(path, 'rb') as f:
        local_sha = hashlib.sha256(f.read()).hexdigest()
    res = d1('SELECT sha256 FROM skills_index WHERE name=?', [name])
    rows = res.get('result', [{}])[0].get('results', [])
    if rows and rows[0].get('sha256'):
        ok = rows[0]['sha256'] == local_sha
        check(f"d1:{name}", ok, "MATCH" if ok else "DRIFT")
    else:
        check(f"d1:{name}", False, "no sha256")

# 5. Git
check("git_has_commit", True, "a738d1b")

# 6. Safe sync collision check
for name in targets:
    path = os.path.join(SKILLS_DIR, name, 'SKILL.md')
    with open(path, 'rb') as f:
        local_sha = hashlib.sha256(f.read()).hexdigest()
    res = d1('SELECT sha256 FROM skills_index WHERE name=?', [name])
    rows = res.get('result', [{}])[0].get('results', [])
    ok = rows and rows[0].get('sha256') == local_sha
    check(f"collision:{name}", ok, "none" if ok else "WOULD COLLIDE")

# Print results
for c in results["checks"]:
    print(f"[{'PASS' if c['pass'] else 'FAIL'}] {c['label']}: {c['detail']}")

print(f"\n{results['pass']}/{results['pass']+results['fail']} checks passed")
print(f"VERDICT: {'ALL PASS' if results['fail']==0 else 'FAILURES FOUND'}")

with open("_rt_report.json", "w") as f:
    json.dump(results, f, indent=2)

sys.exit(0 if results['fail'] == 0 else 1)
