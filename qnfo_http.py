#!/usr/bin/env python3
"""
qnfo_http.py — Standardized HTTP module for QNFO infrastructure.
Eliminates these systemic error classes:
  Class A: Cloudflare WAF 403 blocking Python's default User-Agent
  Class B: SSL context boilerplate (every script has ssl.create_default_context())
  Class C: PowerShell inline Python string mangling (never needed for API calls)
  Class D: Unverified API calls (every call now has retry + timeout)

Usage:
    import qnfo_http
    data = qnfo_http.get('https://qnfo-lifecycle.q08.workers.dev/health')
    data = qnfo_http.get('https://qnfo-data-api.q08.workers.dev/v2/stats')
    result = qnfo_http.post('https://r2-gateway.q08.workers.dev/write', {...})
    ok, msg = qnfo_http.health('https://r2-gateway.q08.workers.dev')

For .py file usage (Rule 13 compliant):
    python -c "import qnfo_http; print(qnfo_http.get('https://...'))"
"""

import urllib.request, urllib.error, json, ssl, time

# === CONFIGURATION ===
USER_AGENT = 'Mozilla/5.0 (QNFO-qnfo_http/1.0)'
DEFAULT_TIMEOUT = 15
MAX_RETRIES = 3
RETRY_DELAY = 1

_SSL_CONTEXT = None

def _ssl():
    """Lazy SSL context — avoids repeated creation."""
    global _SSL_CONTEXT
    if _SSL_CONTEXT is None:
        _SSL_CONTEXT = ssl.create_default_context()
    return _SSL_CONTEXT

def request(url, method='GET', data=None, headers=None, timeout=DEFAULT_TIMEOUT, raw=False):
    """Unified HTTP request with retry, WAF-safe headers, SSL context.
    
    Args:
        url: Full URL to query
        method: GET or POST
        data: Dict for JSON body (POST) or None
        headers: Extra headers (User-Agent added automatically)
        timeout: Request timeout in seconds
        raw: Return raw bytes instead of parsed JSON
    
    Returns:
        Parsed JSON dict, or raw bytes if raw=True
    
    Raises:
        urllib.error.HTTPError on non-2xx status (after retries)
    """
    h = {'User-Agent': USER_AGENT, 'Accept': 'application/json'}
    if headers:
        h.update(headers)
    
    body = None
    if data is not None:
        body = json.dumps(data).encode('utf-8')
        h['Content-Type'] = 'application/json'
    
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, data=body, method=method, headers=h)
            with urllib.request.urlopen(req, timeout=timeout, context=_ssl()) as r:
                result = r.read()
                return result if raw else json.loads(result)
        except urllib.error.HTTPError as e:
            last_error = e
            if e.code == 403:
                # Cloudflare WAF — retry with Firefox UA
                h['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
            elif e.code < 500:
                raise  # Client errors are not retried (except 403)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
        except urllib.error.URLError as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
    
    raise last_error

def get(url, **kwargs):
    """GET request — returns parsed JSON."""
    return request(url, 'GET', **kwargs)

def post(url, data, **kwargs):
    """POST request with JSON body."""
    return request(url, 'POST', data=data, **kwargs)

def health(url, **kwargs):
    """Quick health check — returns (ok_bool, status_dict)."""
    try:
        data = get(url, **kwargs)
        ok = isinstance(data, dict) and data.get('status') == 'ok'
        return ok, data
    except Exception as e:
        return False, {'error': str(e)}

def verify_url(url, expected_status=200):
    """Verify a URL returns expected HTTP status."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=10, context=_ssl()) as r:
            return r.status == expected_status, r.status
    except urllib.error.HTTPError as e:
        return e.code == expected_status, e.code
    except Exception:
        return False, 0
