#!/usr/bin/env python3
"""
r2ctl.py — QNFO R2 Data Catalog CLI v1.0
Unified command-line tool for all 6 R2 buckets via r2-gateway API or direct rclone.

Usage:
  r2ctl.py catalog [bucket] [--prefix P] [--limit N]  List objects
  r2ctl.py buckets                                     Bucket inventory
  r2ctl.py get <bucket>/<key> [--output FILE]          Download object
  r2ctl.py put <local-file> <bucket>/<key>             Upload file
  r2ctl.py search <query>                              Search across buckets
  r2ctl.py info <bucket>/<key>                         Object metadata
  r2ctl.py export <bucket> [--csv]                     Export catalog
  r2ctl.py delete <bucket>/<key>                       Delete object
  r2ctl.py mount <bucket> <drive-letter>               Mount as Windows drive
  r2ctl.py unmount <drive-letter>                      Unmount drive
  r2ctl.py health                                      Health check
  r2ctl.py ui                                          Open catalog in browser

Env: R2_GATEWAY (default: https://r2-gateway.q08.workers.dev)
"""
import os, sys, json, urllib.request, urllib.error, subprocess, webbrowser, argparse

GATEWAY = os.environ.get('R2_GATEWAY', 'https://r2-gateway.q08.workers.dev')
RCLONE = r'C:\Users\LENOVO\AppData\Local\Programs\DeepChat\rclone.exe'
HEADERS = {'User-Agent': 'r2ctl/1.0', 'Accept': 'application/json'}

BUCKETS = ['qnfo-releases','qnfo-skills','qnfo-audit','qnfo-projects','qnfo-backups','qnfo-assets']
BUCKET_LABELS = {'qnfo-releases':'Releases','qnfo-skills':'Skills','qnfo-audit':'Audit','qnfo-projects':'Projects','qnfo-backups':'Backups','qnfo-assets':'Assets'}
BUCKET_RCLONE = {'qnfo-releases':'releases','qnfo-skills':'archive','qnfo-audit':'archive'}

def api(endpoint, method='GET', data=None, raw=False):
    url = f'{GATEWAY}{endpoint}'
    try:
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, method=method, headers=HEADERS)
        if body:
            req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode() if raw else json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        print(f'Error {e.code}: {body}')
        sys.exit(1)
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)

def fmt_size(b):
    if b is None or b < 1024: return f'{b or 0} B'
    for u in ['KB','MB','GB','TB']:
        b /= 1024
        if b < 1024: return f'{b:.1f} {u}'
    return f'{b:.1f} TB'

def cmd_catalog(bucket=None, prefix='', limit=50):
    if bucket:
        r = api(f'/catalog/list?bucket={bucket}&prefix={prefix}&limit={limit}')
        print(f'\n{"="*70}')
        print(f'  {bucket} | {r["count"]} objects | prefix: {prefix or "(root)"}')
        print(f'{"="*70}')
        for o in r['objects']:
            print(f'  {o["key"]:<50s}  {fmt_size(o.get("size")):>10s}')
        if r.get('truncated'):
            print(f'  ... (truncated, use --limit for more)')
    else:
        r = api(f'/catalog?prefix={prefix}&limit={limit}')
        total = 0
        for bname, info in r['results'].items():
            if info.get('count', 0) == 0: continue
            total += info['count']
            print(f'\n--- {bname} ({info["count"]} objects) ---')
            for o in info.get('objects', [])[:10]:
                print(f'  {o["key"]:<50s}  {fmt_size(o.get("size")):>10s}')
        print(f'\nTotal: {total} objects across {len(BUCKETS)} buckets')

def cmd_buckets():
    r = api('/buckets')
    print(f'\n{"="*50}')
    print(f'  QNFO R2 Bucket Fleet ({r["total"]} buckets)')
    print(f'{"="*50}')
    for name in BUCKETS:
        info = r['buckets'].get(name, {})
        desc = BUCKET_LABELS.get(name, '')
        status = info.get('objects', info.get('error', '?'))
        print(f'  {name:<25s} {desc:<25s} {status}')

def cmd_get(path, output=None):
    parts = path.split('/', 1)
    if len(parts) != 2 or parts[0] not in BUCKETS:
        print(f'Usage: r2ctl.py get <bucket>/<key>')
        print(f'  Available buckets: {", ".join(BUCKETS)}')
        sys.exit(1)
    bucket, key = parts
    r = api(f'/get?bucket={bucket}&key={urllib.request.quote(key)}', raw=True)
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(r)
        print(f'Saved: {output} ({len(r)} chars)')
    else:
        print(r[:5000])
        if len(r) > 5000: print(f'... ({len(r)-5000} more chars)')

def cmd_put(local, path):
    parts = path.split('/', 1)
    if len(parts) != 2 or parts[0] not in BUCKETS:
        print(f'Usage: r2ctl.py put <file> <bucket>/<key>')
        sys.exit(1)
    bucket, key = parts
    if not os.path.isfile(local):
        print(f'File not found: {local}')
        sys.exit(1)
    with open(local, 'rb') as f:
        content = f.read()
    r = api('/write', method='POST', data={'key': key, 'bucket': bucket, 'content': content.decode('utf-8', errors='replace'), 'contentType': 'application/octet-stream'})
    if r.get('status') == 'written':
        print(f'✅ Uploaded: {bucket}/{key} ({fmt_size(r.get("sizeBytes", 0))})')
        print(f'   Verified: {r.get("verified", False)}')
    else:
        print(f'❌ Failed: {r}')

def cmd_search(query):
    r = api(f'/search?q={urllib.request.quote(query)}')
    print(f'\nSearch: "{query}" — {r["hits"]} hits')
    for o in r['results']:
        print(f'  {o["bucket"]}/{o["key"]:<60s} {fmt_size(o.get("size"))}')

def cmd_info(path):
    parts = path.split('/', 1)
    if len(parts) != 2 or parts[0] not in BUCKETS:
        print(f'Usage: r2ctl.py info <bucket>/<key>')
        sys.exit(1)
    r = api(f'/info?bucket={parts[0]}&key={urllib.request.quote(parts[1])}')
    print(json.dumps(r, indent=2))

def cmd_export(bucket, csv=False):
    fmt = 'csv' if csv else 'json'
    if csv:
        r = api(f'/export?bucket={bucket}&format=csv', raw=True)
        out = f'{bucket}-catalog.csv'
        with open(out, 'w', encoding='utf-8') as f:
            f.write(r)
        lines = r.count('\n')
        print(f'Exported: {out} ({lines} rows)')
    else:
        r = api(f'/export?bucket={bucket}')
        print(json.dumps(r, indent=2))

def cmd_delete(path):
    parts = path.split('/', 1)
    if len(parts) != 2:
        print(f'Usage: r2ctl.py delete <bucket>/<key>')
        sys.exit(1)
    bucket, key = parts
    confirm = input(f'Delete {bucket}/{key}? [y/N] ')
    if confirm.lower() != 'y':
        print('Cancelled')
        return
    r = api('/delete', method='POST', data={'bucket': bucket, 'key': key})
    print(f'{r["status"]}: {bucket}/{key}')

def cmd_health():
    r = api('/health')
    print(json.dumps(r, indent=2))

def cmd_ui():
    webbrowser.open(GATEWAY + '/ui')

def cmd_mount(bucket, drive):
    if not os.path.isfile(RCLONE):
        print(f'rclone not found at: {RCLONE}')
        print('Download: https://rclone.org/downloads/')
        sys.exit(1)
    mount_path = f'{drive}:\\'
    remote = BUCKET_RCLONE.get(bucket, 'archive')
    print(f'Mounting {bucket} ({remote}) → {mount_path}')
    cmd = f'start "R2-{drive}" "{RCLONE}" mount {remote}: {mount_path} --vfs-cache-mode writes --volname "QNFO-{drive}" --no-console'
    subprocess.Popen(cmd, shell=True)
    print(f'Mounted! Drive {drive}: should appear shortly.')

def cmd_unmount(drive):
    mount_path = f'{drive}:\\'
    print(f'Unmounting {mount_path}')
    subprocess.run(f'"{RCLONE}" unmount {mount_path}', shell=True)
    print(f'Unmounted {drive}:')

def main():
    parser = argparse.ArgumentParser(description='QNFO R2 Data Catalog CLI')
    sub = parser.add_subparsers(dest='cmd')

    p = sub.add_parser('catalog', help='List objects')
    p.add_argument('bucket', nargs='?', help='Bucket name (or all)')
    p.add_argument('--prefix', '-p', default='', help='Key prefix filter')
    p.add_argument('--limit', '-n', type=int, default=50, help='Max results')

    sub.add_parser('buckets', help='Bucket inventory')

    p = sub.add_parser('get', help='Download object')
    p.add_argument('path', help='bucket/key')
    p.add_argument('--output', '-o', help='Save to file')

    p = sub.add_parser('put', help='Upload file')
    p.add_argument('local', help='Local file path')
    p.add_argument('path', help='bucket/key')

    p = sub.add_parser('search', help='Search across buckets')
    p.add_argument('query', help='Search term')

    p = sub.add_parser('info', help='Object metadata')
    p.add_argument('path', help='bucket/key')

    p = sub.add_parser('export', help='Export catalog')
    p.add_argument('bucket', help='Bucket name')
    p.add_argument('--csv', action='store_true', help='Export as CSV')

    p = sub.add_parser('delete', help='Delete object')
    p.add_argument('path', help='bucket/key')

    sub.add_parser('health', help='Health check')
    sub.add_parser('ui', help='Open catalog in browser')

    p = sub.add_parser('mount', help='Mount bucket as drive')
    p.add_argument('bucket', help='Bucket name')
    p.add_argument('drive', help='Drive letter (e.g., A)')

    p = sub.add_parser('unmount', help='Unmount drive')
    p.add_argument('drive', help='Drive letter')

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    cmds = {'catalog': lambda: cmd_catalog(args.bucket, args.prefix, args.limit),
            'buckets': cmd_buckets, 'get': lambda: cmd_get(args.path, args.output),
            'put': lambda: cmd_put(args.local, args.path), 'search': lambda: cmd_search(args.query),
            'info': lambda: cmd_info(args.path), 'export': lambda: cmd_export(args.bucket, args.csv),
            'delete': lambda: cmd_delete(args.path), 'health': cmd_health, 'ui': cmd_ui,
            'mount': lambda: cmd_mount(args.bucket, args.drive), 'unmount': lambda: cmd_unmount(args.drive)}
    cmds[args.cmd]()

if __name__ == '__main__':
    main()
