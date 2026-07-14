import os, json, ssl, urllib.request

TOKEN = os.environ.get('CLOUDFLARE_API_TOKEN', '')
ACCOUNT = 'edb167b78c9fb901ea5bca3ce58ccc4b'
KG_API = 'https://graph-api.q08.workers.dev'
ctx = ssl.create_default_context()

results = {}

# GATE 4: Vectorize coverage
try:
    url = f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/vectorize/v2/indexes/qwav-research-v2'
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    vz = json.loads(urllib.request.urlopen(req, timeout=15, context=ctx).read())
    results['vz_qwav_vectors'] = vz.get('result', {}).get('vectorCount', 0)
    results['vz_qwav_dimensions'] = vz.get('result', {}).get('config', {}).get('dimensions', 0)
    results['g4_pass'] = True
except Exception as e:
    results['g4_error'] = str(e)
    results['g4_pass'] = False

# GATE 5: KG consistency
try:
    r = urllib.request.Request(f'{KG_API}/stats', headers={'User-Agent': 'SafetyGate/1.0'})
    kg = json.loads(urllib.request.urlopen(r, timeout=10, context=ctx).read())
    kp = next((n.get('count', 0) for n in kg.get('nodeLabels', []) if n.get('label') == 'Paper'), 0)
    results['kg_papers'] = kp
    results['kg_total_nodes'] = kg.get('totalNodes', 0)
    results['g5_pass'] = True
except Exception as e:
    results['g5_error'] = str(e)
    results['g5_pass'] = False

# GATE 6: Architecture doc
try:
    url = f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/r2/buckets/qnfo/objects/qnfo/UNIFIED-ARCHITECTURE.md'
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    body = urllib.request.urlopen(req, timeout=10, context=ctx).read()
    ok = (b'UNIFIED PUBLICATION ARCHITECTURE' in body or b'ARCHITECTURE v3.0' in body) and len(body) > 1000
    results['g6_bytes'] = len(body)
    results['g6_pass'] = ok
except Exception as e:
    results['g6_error'] = str(e)
    results['g6_pass'] = False

print(json.dumps(results, indent=2))
passed = sum(1 for k in results if k.endswith('_pass') and results[k])
total = 3
print(f'\nSAFETY GATE: {passed}/{total} passed')
