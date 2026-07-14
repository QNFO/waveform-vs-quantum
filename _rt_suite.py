import json, ssl, urllib.request
"""QNFO Red-Team Test Suite — Infrastructure Health"""

ctx = ssl.create_default_context()
results = {}
passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        results[name] = "PASS"
    else:
        failed += 1
        results[name] = f"FAIL: {detail}"

# T1: Worker health checks
print("## WORKER HEALTH")
for name, url in [
    ("search-worker", "https://search-worker.q08.workers.dev/health"),
    ("qnfo-memory-mcp", "https://qnfo-memory-mcp.q08.workers.dev/health"),
    ("qnfo-ai-worker", "https://qnfo-ai-worker.q08.workers.dev/health"),
]:
    try:
        r = urllib.request.Request(url, headers={"User-Agent": "RedTeam/1.0"})
        data = json.loads(urllib.request.urlopen(r, timeout=10, context=ctx).read())
        test(f"health/{name}", data.get("status") == "ok", str(data))
    except Exception as e:
        test(f"health/{name}", False, str(e)[:100])

# T2: API endpoint tests
print("## API ENDPOINTS")
try:
    r = urllib.request.Request("https://search-worker.q08.workers.dev/api/search/papers?q=test&limit=1", headers={"User-Agent": "RedTeam/1.0"})
    data = json.loads(urllib.request.urlopen(r, timeout=10, context=ctx).read())
    test("api/search_papers_works", "error" not in data, str(data)[:80])
except Exception as e:
    test("api/search_papers_works", False, str(e)[:100])

try:
    r = urllib.request.Request("https://graph-api.q08.workers.dev/stats", headers={"User-Agent": "RedTeam/1.0"})
    data = json.loads(urllib.request.urlopen(r, timeout=10, context=ctx).read())
    test("api/graph_stats", data.get("totalNodes", 0) > 1000, f"nodes={data.get('totalNodes')}")
except Exception as e:
    test("api/graph_stats", False, str(e)[:100])

# T3: MCP endpoint tests
print("## MCP PROTOCOL")
try:
    body = json.dumps({"jsonrpc":"2.0","method":"tools/list","id":1}).encode()
    r = urllib.request.Request("https://qnfo-memory-mcp.q08.workers.dev/mcp", data=body, method="POST", headers={"Content-Type":"application/json"})
    data = json.loads(urllib.request.urlopen(r, timeout=15, context=ctx).read())
    tools = [t["name"] for t in data.get("result",{}).get("tools",[])]
    test("mcp/tools_list", len(tools) == 6, f"tools={tools}")
except Exception as e:
    test("mcp/tools_list", False, str(e)[:100])

# MCP remember_fact + recall_facts cycle
try:
    body = json.dumps({"jsonrpc":"2.0","method":"tools/call","params":{"name":"remember_fact","arguments":{"content":"RED-TEAM E2E TEST: D1+Vectorize write","category":"project_fact","importance":1.0}},"id":200}).encode()
    r = urllib.request.Request("https://qnfo-memory-mcp.q08.workers.dev/mcp", data=body, method="POST", headers={"Content-Type":"application/json"})
    data = json.loads(urllib.request.urlopen(r, timeout=30, context=ctx).read())
    storage = json.loads(data.get("result",{}).get("content",[{}])[0].get("text","{}")).get("storage",{})
    test("mcp/e2e_remember", storage.get("d1") == True and storage.get("vectorize") == True, str(storage))
except Exception as e:
    test("mcp/e2e_remember", False, str(e)[:100])

try:
    body = json.dumps({"jsonrpc":"2.0","method":"tools/call","params":{"name":"recall_facts","arguments":{"limit":10}},"id":201}).encode()
    r = urllib.request.Request("https://qnfo-memory-mcp.q08.workers.dev/mcp", data=body, method="POST", headers={"Content-Type":"application/json"})
    data = json.loads(urllib.request.urlopen(r, timeout=15, context=ctx).read())
    facts = json.loads(data.get("result",{}).get("content",[{}])[0].get("text","{}")).get("facts",[])
    test("mcp/e2e_recall", len(facts) >= 1, f"count={len(facts)}")
except Exception as e:
    test("mcp/e2e_recall", False, str(e)[:100])

# T4: Vectorize indices
print("## VECTORIZE INDICES")
import os
TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN","")
ACCOUNT = "edb167b78c9fb901ea5bca3ce58ccc4b"
for idx, dims in [("qnfo-handoffs",768),("qwav-research-v2",768)]:
    try:
        url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/vectorize/v2/indexes/{idx}"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {TOKEN}")
        data = json.loads(urllib.request.urlopen(req, timeout=10, context=ctx).read())
        actual_dims = data.get("result",{}).get("config",{}).get("dimensions",0)
        count = data.get("result",{}).get("vectorCount",0)
        test(f"vz/{idx}_dims", actual_dims == dims, f"expected={dims} actual={actual_dims}")
        test(f"vz/{idx}_exists", "error" not in data, f"vectors={count}")
    except Exception as e:
        test(f"vz/{idx}", False, str(e)[:100])

print(f"\n{'='*50}")
print(f"RESULTS: {passed}/{passed+failed} passed, {failed} failed")
for name, result in sorted(results.items()):
    print(f"  [{result[:4]}] {name}: {result[5:] if result.startswith('FAIL') else ''}")
