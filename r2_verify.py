"""
r2_verify.py — R2 Write-Verify Protocol
Eliminates: phantom uploads, wrangler stdout trust issues, unverified writes.

Usage:
    import r2_verify
    r2_verify.verify_write(gateway_url, bucket, key, expected_size)
    r2_verify.verify_path(gateway_url, paths_dict)

Protocol: WRITE → GET → COMPARE → CONFIRM (never: WRITE → hope)
"""

import urllib.request, urllib.error, json, time, hashlib

USER_AGENT = 'Mozilla/5.0 (QNFO-r2_verify/1.0)'
RETRIES = 3
RETRY_DELAY = 1

def verify_write(gateway, bucket, key, expected_size, content_hash=None):
    """Verify an R2 object exists and has correct size after write.
    
    Args:
        gateway: r2-gateway URL (e.g., 'https://r2-gateway.q08.workers.dev')
        bucket: Bucket name
        key: Object key
        expected_size: Expected bytes
    
    Returns:
        (verified: bool, details: dict)
    """
    for attempt in range(RETRIES):
        try:
            url = f'{gateway}/get?bucket={bucket}&key={urllib.request.quote(key)}'
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = r.read()
                actual_size = len(data)
                
                verified = actual_size == expected_size
                details = {
                    'key': f'{bucket}/{key}',
                    'expected_size': expected_size,
                    'actual_size': actual_size,
                    'verified': verified,
                    'attempt': attempt + 1,
                    'status': 'verified' if verified else 'size_mismatch'
                }
                
                if verified and content_hash:
                    actual_hash = hashlib.sha256(data).hexdigest()
                    details['expected_hash'] = content_hash
                    details['actual_hash'] = actual_hash
                    details['verified'] = actual_hash == content_hash
                    if not details['verified']:
                        details['status'] = 'hash_mismatch'
                
                if verified:
                    return verified, details
                
        except urllib.error.HTTPError as e:
            if e.code == 404:
                details = {
                    'key': f'{bucket}/{key}',
                    'expected_size': expected_size,
                    'actual_size': 0,
                    'verified': False,
                    'attempt': attempt + 1,
                    'status': 'not_found'
                }
            else:
                details = {'error': f'HTTP {e.code}', 'attempt': attempt + 1, 'status': 'error'}
        except Exception as e:
            details = {'error': str(e), 'attempt': attempt + 1, 'status': 'error'}
        
        if attempt < RETRIES - 1:
            time.sleep(RETRY_DELAY * (attempt + 1))
    
    return False, details


def verify_path(gateway, paths):
    """Verify multiple R2 objects exist.
    
    Args:
        gateway: r2-gateway URL
        paths: dict of {key: bucket} pairs or dict of {key: (bucket, expected_size)}
    
    Returns:
        dict with {verified: N, total: M, results: [...]}
    """
    results = {'verified': 0, 'failed': 0, 'total': len(paths), 'results': []}
    
    for key, info in paths.items():
        if isinstance(info, tuple):
            bucket, size = info
        else:
            bucket = info
            size = None
        
        try:
            url = f'{gateway}/info?bucket={bucket}&key={urllib.request.quote(key)}'
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
                actual_size = data.get('size', 0)
                
                entry = {
                    'key': f'{bucket}/{key}',
                    'size': actual_size,
                    'status': 'ok'
                }
                
                if size is not None:
                    if actual_size == size:
                        entry['verified'] = True
                        results['verified'] += 1
                    else:
                        entry['verified'] = False
                        entry['expected_size'] = size
                        results['failed'] += 1
                else:
                    results['verified'] += 1
                
                results['results'].append(entry)
                
        except urllib.error.HTTPError as e:
            entry = {'key': f'{bucket}/{key}', 'status': f'HTTP {e.code}', 'verified': False}
            results['results'].append(entry)
            results['failed'] += 1
        except Exception as e:
            entry = {'key': f'{bucket}/{key}', 'status': str(e)[:100], 'verified': False}
            results['results'].append(entry)
            results['failed'] += 1
    
    return results


def scan_bucket(gateway, bucket, prefix='', limit=100):
    """Scan a bucket and return all object keys and sizes.
    
    Args:
        gateway: r2-gateway URL
        bucket: Bucket name
        prefix: Key prefix filter
        limit: Max objects to return
    
    Returns:
        list of {key, size} dicts
    """
    try:
        url = f'{gateway}/catalog/list?bucket={bucket}&prefix={urllib.request.quote(prefix)}&limit={limit}'
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
            return data.get('objects', [])
    except Exception as e:
        print(f'Error scanning {bucket}: {e}')
        return []
