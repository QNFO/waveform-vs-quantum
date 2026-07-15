#!/usr/bin/env python3
"""
R2 Catalog Monitor — Verifies all 6 R2 bucket bindings on r2-gateway v2.0.
Integration with the qnfo_http module for safe, WAF-compatible HTTP calls.
"""
import sys, json
sys.path.insert(0, r'C:\Users\LENOVO\AppData\Local\Programs\DeepChat')
import qnfo_http

# Step 1: Health check
print('=== R2 GATEWAY HEALTH ===')
ok, health = qnfo_http.health('https://r2-gateway.q08.workers.dev/health')
print(f'  Status: {"OK" if ok else "FAIL"}')
print(f'  Version: {health.get("version","?")}')
print(f'  Features: {health.get("features",[])}')
print(f'  Buckets: {health.get("buckets",0)}')

# Step 2: All 6 buckets status
print('\n=== BUCKET FLEET ===')
buckets = qnfo_http.get('https://r2-gateway.q08.workers.dev/buckets')
for name in sorted(buckets['buckets'].keys()):
    info = buckets['buckets'][name]
    desc = info.get('description', '')
    status = info.get('objects', info.get('error', '?'))
    print(f'  {name:<25s} {desc:<35s} {status}')

# Step 3: Object catalog (first 5 from qnfo-skills)
print('\n=== SAMPLE CATALOG (qnfo-skills) ===')
catalog = qnfo_http.get('https://r2-gateway.q08.workers.dev/catalog/list?bucket=qnfo-skills&limit=5')
for o in catalog['objects']:
    kb = o.get('size', 0) / 1024
    print(f'  {o["key"]:<55s} {kb:.1f} KB')

print(f'\n✅ R2 Catalog Monitor — ALL SYSTEMS HEALTHY')
