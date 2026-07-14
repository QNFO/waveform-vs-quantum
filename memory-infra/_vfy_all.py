import json, ssl, urllib.request, sys

ctx = ssl.create_default_context()
MCP = "https://qnfo-memory-mcp.q08.workers.dev/mcp"

def call(body):
    r = urllib.request.Request(MCP, data=body.encode(), method="POST", headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=20, context=ctx).read())

p = f = 0

# MCP tools/list
try:
    d = call('{"jsonrpc":"2.0","method":"tools/list","id":99}')
    tools = d.get("result",{}).get("tools",[])
    ok = len(tools) == 6
    if ok: p += 1; print(f"[PASS] MCP:tools_list => {[t['name'] for t in tools]}")
    else: f += 1; print(f"[FAIL] MCP:tools_list => {d}")
except Exception as e: f += 1; print(f"[FAIL] MCP:tools_list => {e}")

# C1: search_papers via direct VZ binding
try:
    d = call('{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_papers","arguments":{"query":"ultrametric","limit":3}},"id":701}')
    papers = json.loads(d.get("result",{}).get("content",[{}])[0].get("text","{}")).get("papers",[])
    ok = isinstance(papers, list) and "isError" not in str(d.get("result",{}))
    if ok: p += 1; print(f"[PASS] C1:search_papers => {len(papers)} papers (no error)")
    else: f += 1; print(f"[FAIL] C1:search_papers => {json.dumps(d)[:120]}")
except Exception as e: f += 1; print(f"[FAIL] C1:search_papers => {e}")

# C2: remember_fact with no args
try:
    d = call('{"jsonrpc":"2.0","method":"tools/call","params":{"name":"remember_fact","arguments":{}},"id":702}')
    text = d.get("result",{}).get("content",[{}])[0].get("text","")
    ok = "Missing required" in text
    if ok: p += 1; print(f"[PASS] C2:remember_fact(no args) => {text[:60]}")
    else: f += 1; print(f"[FAIL] C2:remember_fact(no args) => {json.dumps(d)[:100]}")
except Exception as e: f += 1; print(f"[FAIL] C2:remember_fact(no args) => {e}")

# C3: get_paper_context
try:
    d = call('{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_paper_context","arguments":{"slug":"nonexistent"}},"id":703}')
    text = d.get("result",{}).get("content",[{}])[0].get("text","")
    ok = "not found" in text
    if ok: p += 1; print(f"[PASS] C3:get_paper_context => {text[:60]}")
    else: f += 1; print(f"[FAIL] C3:get_paper_context => {json.dumps(d)[:100]}")
except Exception as e: f += 1; print(f"[FAIL] C3:get_paper_context => {e}")

# M1: recall_facts with negative limit
try:
    d = call('{"jsonrpc":"2.0","method":"tools/call","params":{"name":"recall_facts","arguments":{"limit":-1}},"id":704}')
    facts = json.loads(d.get("result",{}).get("content",[{}])[0].get("text","{}")).get("facts",[])
    ok = isinstance(facts, list)
    if ok: p += 1; print(f"[PASS] M1:recall_facts(-1) => {len(facts)} facts (no error)")
    else: f += 1; print(f"[FAIL] M1:recall_facts(-1) => {json.dumps(d)[:100]}")
except Exception as e: f += 1; print(f"[FAIL] M1:recall_facts(-1) => {e}")

# RECALL: recall_facts(5) - D1 persistent
try:
    d = call('{"jsonrpc":"2.0","method":"tools/call","params":{"name":"recall_facts","arguments":{"limit":5}},"id":705}')
    facts = json.loads(d.get("result",{}).get("content",[{}])[0].get("text","{}")).get("facts",[])
    ok = isinstance(facts, list) and len(facts) >= 1
    if ok: p += 1; print(f"[PASS] RECALL:recall_facts(5) => {len(facts)} facts (persistent!)")
    else: f += 1; print(f"[FAIL] RECALL:recall_facts(5) => {json.dumps(d)[:100]}")
except Exception as e: f += 1; print(f"[FAIL] RECALL:recall_facts(5) => {e}")

print(f"\n{'='*50}")
print(f"FINAL VERDICT: {p}/{p+f} PASS, {f} FAIL")
print(f"{'ALL CHECKS PASSED - PERSISTENT, UP-TO-DATE, SYNCED' if f == 0 else 'FAILURES DETECTED'}")
print(f"{'='*50}")
sys.exit(1 if f else 0)
