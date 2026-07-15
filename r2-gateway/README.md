# r2-gateway Worker

Centralized R2 write gateway for QNFO 6-bucket fleet.

## Deploy

`ash
cd r2-gateway
npx wrangler secret put API_TOKEN
npx wrangler deploy
`

## API

| Endpoint | Method | Purpose |
|:---------|:------|:--------|
| /health | GET | Health check |
| /routes | GET | Bucket routing table |
| /resolve | POST | Dry-run key→bucket resolution |
| /write | POST | Validated write with lock+verify |

## Architecture

See R2-MULTI-BUCKET-ARCHITECTURE.md
