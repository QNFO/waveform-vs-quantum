# =============================================================================
# R2 Archive Uploader — Environment Setup
# =============================================================================
# Run this ONCE before using r2_archive_upload.py.
# It will prompt you for your R2 API token credentials and persist them
# as user-level environment variables.
#
# HOW TO GET YOUR R2 API TOKEN:
#   1. Go to: https://dash.cloudflare.com/edb167b78c9fb901ea5bca3ce58ccc4b/r2/api-tokens
#   2. Click "Manage API Tokens" → "Create API Token"
#   3. Choose "Object Read & Write" permission
#   4. Scope to bucket "archive" (or leave unscoped for all buckets)
#   5. Copy the Access Key ID and Secret Access Key
#   6. Run this script and paste them when prompted
# =============================================================================

param(
    [switch]$Show   # Show current values (masked)
)

$accountId = "edb167b78c9fb901ea5bca3ce58ccc4b"
$bucket    = "archive"

if ($Show) {
    Write-Host "`nCurrent R2 environment variables:" -ForegroundColor Cyan
    Write-Host "  R2_ACCOUNT_ID         = $env:R2_ACCOUNT_ID"
    Write-Host "  R2_BUCKET             = $env:R2_BUCKET"
    if ($env:R2_ACCESS_KEY_ID) {
        $masked = $env:R2_ACCESS_KEY_ID.Substring(0, [Math]::Min(8, $env:R2_ACCESS_KEY_ID.Length)) + "..."
        Write-Host "  R2_ACCESS_KEY_ID      = $masked"
    } else {
        Write-Host "  R2_ACCESS_KEY_ID      = (not set)"
    }
    if ($env:R2_SECRET_ACCESS_KEY) {
        Write-Host "  R2_SECRET_ACCESS_KEY  = ********"
    } else {
        Write-Host "  R2_SECRET_ACCESS_KEY  = (not set)"
    }
    exit 0
}

Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║         R2 Archive Uploader — Credential Setup               ║
╚══════════════════════════════════════════════════════════════╝

This script sets persistent environment variables for R2 access.
You need an R2 API token. Create one here:
  https://dash.cloudflare.com/$accountId/r2/api-tokens

Bucket: $bucket
Account: $accountId

"@ -ForegroundColor White

# --- R2_ACCESS_KEY_ID ---
$accessKey = Read-Host "Paste R2 Access Key ID"
if (-not $accessKey) {
    Write-Host "ERROR: Access Key ID is required." -ForegroundColor Red
    exit 1
}

# --- R2_SECRET_ACCESS_KEY ---
$secretKey = Read-Host "Paste R2 Secret Access Key" -AsSecureString
if ($secretKey.Length -eq 0) {
    Write-Host "ERROR: Secret Access Key is required." -ForegroundColor Red
    exit 1
}
$secretPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secretKey)
)

# --- Set user-level environment variables ---
Write-Host "`nSetting environment variables..." -ForegroundColor Yellow

[Environment]::SetEnvironmentVariable("R2_ACCESS_KEY_ID", $accessKey, "User")
[Environment]::SetEnvironmentVariable("R2_SECRET_ACCESS_KEY", $secretPlain, "User")
[Environment]::SetEnvironmentVariable("R2_ACCOUNT_ID", $accountId, "User")
[Environment]::SetEnvironmentVariable("R2_BUCKET", $bucket, "User")

# Also set in current session
$env:R2_ACCESS_KEY_ID     = $accessKey
$env:R2_SECRET_ACCESS_KEY = $secretPlain
$env:R2_ACCOUNT_ID        = $accountId
$env:R2_BUCKET            = $bucket

Write-Host @"

✅ Credentials saved!
   Variables set for: current session + all future sessions (User scope)

Next steps:
   1. Install dependencies:  pip install boto3 tqdm
   2. Dry-run to audit:      python r2_archive_upload.py --dry-run
   3. Start upload:          python r2_archive_upload.py
   4. Resume after interrupt: python r2_archive_upload.py   (just run again)

"@ -ForegroundColor Green
