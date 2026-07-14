#!/usr/bin/env python3
"""Sync modified skills to R2 backup — prompt audit cross-reference session."""
import os, json, ssl, urllib.request

TOKEN = os.environ.get('CLOUDFLARE_API_TOKEN', '')
ACCOUNT = 'edb167b78c9fb901ea5bca3ce58ccc4b'
SKILLS_DIR = os.path.expandvars(r'%USERPROFILE%\.deepchat\skills')
BUCKET = 'qnfo'
PREFIX = 'qnfo/prompts/skills'

SKILLS = ['closeout-manager', 'execution-guard', 'qnfo-agent', 'research-planner']
ctx = ssl.create_default_context()

def upload_skill(name):
    local = os.path.join(SKILLS_DIR, name, 'SKILL.md')
    size = os.path.getsize(local)
    key = f'{PREFIX}/{name}/SKILL.md'
    url = f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/r2/buckets/{BUCKET}/objects/{key}'
    
    with open(local, 'rb') as f:
        data = f.read()
    
    req = urllib.request.Request(url, method='PUT', data=data)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Content-Type', 'application/octet-stream')
    
    resp = urllib.request.urlopen(req, timeout=30, context=ctx)
    result = json.loads(resp.read())
    ok = result.get('success', False)
    print(f'  {name}: {"UPLOADED" if ok else "FAILED"} ({size:,} bytes)')
    return ok

print('Syncing 4 modified skills to R2...')
results = {}
for s in SKILLS:
    results[s] = upload_skill(s)

ok = sum(1 for v in results.values() if v)
print(f'\nSynced: {ok}/{len(SKILLS)}')
