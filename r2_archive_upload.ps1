<#
.SYNOPSIS
    One-click archive uploader: copies D:\Archive → Cloudflare R2 `archive` bucket.
    Uses rclone (auto-downloaded) with embedded credentials — no setup required.

.DESCRIPTION
    Features:
      - Progress bars (per-file + aggregate)
      - Resume after interruption (rclone skips already-copied files)
      - Post-upload verification (size comparison)
      - Retry on transient errors
      - Parallel transfers (4 simultaneous files)

    PREREQUISITES: None. rclone.exe is auto-downloaded. Just run this script.

.EXAMPLE
    .\r2_archive_upload.ps1
    .\r2_archive_upload.ps1 -Source "E:\Backups" -Transfers 8
    .\r2_archive_upload.ps1 -DryRun
    .\r2_archive_upload.ps1 -VerifyOnly
#>

[CmdletBinding()]
param(
    [string]$Source = "D:\Archive",
    [int]$Transfers = 4,
    [switch]$DryRun,
    [switch]$VerifyOnly,
    [switch]$SkipVerification,
    [int]$Retries = 5
)

# =============================================================================
# EMBEDDED R2 CREDENTIALS (created 2026-07-15 for archive bucket)
# =============================================================================
$Script:R2_ACCESS_KEY_ID     = "f9bd5c791626bba9cd04a7571ea6e69e"
$Script:R2_SECRET_ACCESS_KEY = "be270e902eb400a193b18d39758037ada78501c284d4b770542e9a56051bf974"
$Script:R2_ACCOUNT_ID        = "edb167b78c9fb901ea5bca3ce58ccc4b"
$Script:R2_BUCKET            = "archive"
$Script:R2_ENDPOINT          = "https://edb167b78c9fb901ea5bca3ce58ccc4b.r2.cloudflarestorage.com"
$Script:RCLONE_REMOTE_NAME   = "archive"

# =============================================================================
# CONFIG
# =============================================================================
$Script:RCLONE_EXE    = Join-Path $PSScriptRoot "rclone.exe"
$Script:RCLONE_ZIP    = Join-Path $PSScriptRoot "rclone.zip"
$Script:RCLONE_URL    = "https://downloads.rclone.org/rclone-current-windows-amd64.zip"
$Script:LOG_FILE      = Join-Path $PSScriptRoot "r2_archive_upload.log"
$Script:START_TIME    = Get-Date
$Script:RCLONE_FLAGS  = @(
    "--progress",
    "--stats", "30s",
    "--size-only",
    "--transfers", $Transfers,
    "--retries", $Retries,
    "--low-level-retries", "10",
    "--no-update-modtime",
    "--ignore-errors",
    "--log-file", $Script:LOG_FILE,
    "--log-level", "INFO"
)

# =============================================================================
# FUNCTIONS
# =============================================================================

function Write-Banner {
    Write-Host @"

╔══════════════════════════════════════════════════════════════════════╗
║           R2 Archive Uploader  —  D:\Archive → R2 archive            ║
╚══════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan
    Write-Host "  Source:   $Source"
    Write-Host "  Target:   $($Script:R2_BUCKET) @ $($Script:R2_ENDPOINT)"
    Write-Host "  Workers:  $Transfers parallel transfers"
    Write-Host "  Retries:  $Retries per file"
    Write-Host ""
}

function Write-Step {
    param([string]$Text, [string]$Color = "White")
    $ts = (Get-Date) - $Script:START_TIME
    $elapsed = "[+{0:mm\:ss}]" -f $ts
    Write-Host "$elapsed  $Text" -ForegroundColor $Color
}

function Download-Rclone {
    if (Test-Path $Script:RCLONE_EXE) {
        Write-Step "rclone.exe found at $($Script:RCLONE_EXE)" "Green"
        $ver = & $Script:RCLONE_EXE version --check 2>&1 | Select-Object -First 1
        Write-Step "  $ver" "DarkGray"
        return $true
    }

    Write-Step "Downloading rclone (portable, ~40 MB)..." "Yellow"
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $Script:RCLONE_URL -OutFile $Script:RCLONE_ZIP -UseBasicParsing

        Write-Step "Extracting rclone.exe..." "Yellow"
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zip = [System.IO.Compression.ZipFile]::OpenRead($Script:RCLONE_ZIP)
        $entry = $zip.Entries | Where-Object { $_.Name -eq "rclone.exe" } | Select-Object -First 1
        if (-not $entry) {
            throw "rclone.exe not found in the downloaded zip"
        }
        [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $Script:RCLONE_EXE, $true)
        $zip.Dispose()
        Remove-Item $Script:RCLONE_ZIP -Force

        Write-Step "rclone.exe ready!" "Green"
        & $Script:RCLONE_EXE version --check 2>&1 | Select-Object -First 1 | ForEach-Object { Write-Step "  $_" "DarkGray" }
        return $true
    }
    catch {
        Write-Step "FAILED to download rclone: $_" "Red"
        Write-Step "Please download manually from https://rclone.org/downloads/ and place rclone.exe in $PSScriptRoot" "Yellow"
        return $false
    }
}

function Initialize-RcloneConfig {
    # Configure via environment variables — no config file needed
    $env:RCLONE_CONFIG = ""
    $env:RCLONE_CONFIG_ARCHIVE_TYPE = "s3"
    $env:RCLONE_CONFIG_ARCHIVE_PROVIDER = "Cloudflare"
    $env:RCLONE_CONFIG_ARCHIVE_ENDPOINT = $Script:R2_ENDPOINT
    $env:RCLONE_CONFIG_ARCHIVE_ACCESS_KEY_ID = $Script:R2_ACCESS_KEY_ID
    $env:RCLONE_CONFIG_ARCHIVE_SECRET_ACCESS_KEY = $Script:R2_SECRET_ACCESS_KEY
    $env:RCLONE_CONFIG_ARCHIVE_REGION = "auto"
    $env:RCLONE_CONFIG_ARCHIVE_ACL = "private"
    Write-Step "rclone remote 'archive' configured via env vars" "Green"
}

function Scan-Source {
    Write-Step "Scanning $Source ..." "Cyan"
    if (-not (Test-Path $Source)) {
        Write-Step "ERROR: Source directory not found: $Source" "Red"
        exit 1
    }
    $files = Get-ChildItem -Path $Source -File -Recurse -ErrorAction SilentlyContinue
    $count = $files.Count
    $totalSize = ($files | Measure-Object -Property Length -Sum).Sum
    $dirCount = ($files | Group-Object Directory).Count
    Write-Step "  $count files across $dirCount folders, total $(Format-Size $totalSize)" "Cyan"
    return @{ Count = $count; Size = $totalSize }
}

function Format-Size {
    param([long]$Bytes)
    if ($Bytes -ge 1TB) { "{0:N2} TB" -f ($Bytes / 1TB) }
    elseif ($Bytes -ge 1GB) { "{0:N2} GB" -f ($Bytes / 1GB) }
    elseif ($Bytes -ge 1MB) { "{0:N2} MB" -f ($Bytes / 1MB) }
    elseif ($Bytes -ge 1KB) { "{0:N2} KB" -f ($Bytes / 1KB) }
    else { "$Bytes B" }
}

function Format-Duration {
    param([TimeSpan]$Duration)
    if ($Duration.TotalHours -ge 1) {
        "{0}h {1}m {2}s" -f [math]::Floor($Duration.TotalHours), $Duration.Minutes, $Duration.Seconds
    }
    elseif ($Duration.TotalMinutes -ge 1) {
        "{0}m {1}s" -f [math]::Floor($Duration.TotalMinutes), $Duration.Seconds
    }
    else {
        "{0}s" -f [math]::Floor($Duration.TotalSeconds)
    }
}

function Invoke-RcloneCopy {
    Write-Step "`n=== STARTING UPLOAD ===" "Magenta"
    Write-Step "Resume-safe: already-uploaded files will be skipped" "DarkGray"
    Write-Host ""

    $copyStart = Get-Date
    $args = @(
        "copy",
        $Source,
        "${Script:RCLONE_REMOTE_NAME}:$($Script:R2_BUCKET)",
        "--check-first"  # list remote first to skip existing files
    ) + $Script:RCLONE_FLAGS

    if ($DryRun) {
        $args += "--dry-run"
        Write-Step "DRY RUN MODE — no files will be transferred" "Yellow"
    }

    Write-Step "Command: rclone $($args -join ' ')" "DarkGray"
    Write-Host ""

    $proc = Start-Process -FilePath $Script:RCLONE_EXE -ArgumentList $args `
        -NoNewWindow -Wait -PassThru

    $copyDuration = (Get-Date) - $copyStart
    Write-Step "Upload phase completed in $(Format-Duration $copyDuration)" "Cyan"

    return $proc.ExitCode
}

function Invoke-RcloneCheck {
    Write-Step "`n=== VERIFYING UPLOAD ===" "Magenta"
    Write-Step "Comparing local file sizes against remote..." "DarkGray"
    Write-Host ""

    $checkStart = Get-Date
    $args = @(
        "check",
        $Source,
        "${Script:RCLONE_REMOTE_NAME}:$($Script:R2_BUCKET)",
        "--size-only",
        "--one-way",
        "--missing-on-dst", "$(Join-Path $PSScriptRoot "r2_missing_files.txt")",
        "--error", "$(Join-Path $PSScriptRoot "r2_error_files.txt")"
    ) + $Script:RCLONE_FLAGS

    $proc = Start-Process -FilePath $Script:RCLONE_EXE -ArgumentList $args `
        -NoNewWindow -Wait -PassThru

    $checkDuration = (Get-Date) - $checkStart
    Write-Step "Verification completed in $(Format-Duration $checkDuration)" "Cyan"

    return $proc.ExitCode
}

function Show-FinalReport {
    param(
        [hashtable]$ScanResult,
        [int]$CopyExitCode,
        [int]$CheckExitCode,
        [TimeSpan]$TotalDuration
    )

    # Parse rclone log for transfer stats (use last match in multi-run log)
    $logContent = ""
    if (Test-Path $Script:LOG_FILE) {
        $logContent = Get-Content $Script:LOG_FILE -Raw -ErrorAction SilentlyContinue
    }

    # Count missing files from verification
    $missingCount = 0
    $missingFile = Join-Path $PSScriptRoot "r2_missing_files.txt"
    if (Test-Path $missingFile) {
        $missingCount = (Get-Content $missingFile | Where-Object { $_ -match '\S' }).Count
    }

    $errorCount = 0
    $errorFile = Join-Path $PSScriptRoot "r2_error_files.txt"
    if (Test-Path $errorFile) {
        $errorCount = (Get-Content $errorFile | Where-Object { $_ -match '\S' }).Count
    }

    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                        FINAL REPORT                                  ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Source:         $Source"
    Write-Host "  Files scanned:  $($ScanResult.Count)"
    Write-Host "  Total size:     $(Format-Size $ScanResult.Size)"
    Write-Host "  Total time:     $(Format-Duration $TotalDuration)"
    Write-Host ""

    if ($CopyExitCode -eq 0) {
        Write-Host "  [PASS]  Upload completed without errors" -ForegroundColor Green
    }
    elseif ($CopyExitCode -le 3) {
        Write-Host "  [WARN]  Upload completed with minor errors (exit code $CopyExitCode)" -ForegroundColor Yellow
    }
    else {
        Write-Host "  [FAIL]  Upload had critical errors (exit code $CopyExitCode)" -ForegroundColor Red
    }

    if (-not $SkipVerification) {
        if ($CheckExitCode -eq 0 -and $missingCount -eq 0) {
            Write-Host "  [PASS]  Verification: all files match" -ForegroundColor Green
        }
        elseif ($missingCount -gt 0) {
            Write-Host "  [FAIL]  Verification: $missingCount file(s) missing on remote" -ForegroundColor Red
            Write-Host "          See: $missingFile" -ForegroundColor DarkGray
        }
        elseif ($CheckExitCode -ne 0) {
            Write-Host "  [WARN]  Verification: differences found (exit $CheckExitCode, $errorCount errors)" -ForegroundColor Yellow
            Write-Host "          See: $errorFile" -ForegroundColor DarkGray
        }
        else {
            Write-Host "  [PASS]  Verification: all files accounted for" -ForegroundColor Green
        }
    }
    else {
        Write-Host "  [SKIP]  Verification skipped (--SkipVerification)" -ForegroundColor DarkGray
    }

    Write-Host ""
    Write-Host "  Log file: $Script:LOG_FILE" -ForegroundColor DarkGray

    # Extract transfer stats from log — get the LAST rclone run's stats
    if ($logContent -match 'Transferred:') {
        $allMatches = [regex]::Matches($logContent, 'Transferred:\s+([\d.]+\s+\S+)\s+/\s+([\d.]+\s+\S+)')
        if ($allMatches.Count -gt 0) {
            $lastMatch = $allMatches[$allMatches.Count - 1]
            Write-Host "  Transferred: $($lastMatch.Groups[1].Value) / $($lastMatch.Groups[2].Value)" -ForegroundColor DarkGray
        }
    }
    if ($logContent -match 'Elapsed time:') {
        $allEt = [regex]::Matches($logContent, 'Elapsed time:\s+([\d.]+[a-z]*)')
        if ($allEt.Count -gt 0) {
            $lastEt = $allEt[$allEt.Count - 1]
            Write-Host "  Rclone reported: $($lastEt.Groups[1].Value.Trim())" -ForegroundColor DarkGray
        }
    }

    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    if ($CopyExitCode -le 3 -and ($SkipVerification -or $missingCount -eq 0)) {
        Write-Host "║  ✓  DONE. Re-run this script to pick up any remaining files.        ║" -ForegroundColor Green
    }
    else {
        Write-Host "║  ⚠  ISSUES DETECTED. Re-run this script to retry.                  ║" -ForegroundColor Yellow
    }
    Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
}

# =============================================================================
# MAIN
# =============================================================================

Clear-Host
Write-Banner

# Clear log from previous runs
"" | Out-File -FilePath $Script:LOG_FILE -Encoding utf8 -Force

# Step 1: Download rclone
Write-Step "Step 1/4: Checking rclone..." "White"
if (-not (Download-Rclone)) {
    exit 1
}

# Step 2: Configure rclone
Write-Step "Step 2/4: Configuring rclone..." "White"
Initialize-RcloneConfig

# Step 3: Scan source
Write-Step "Step 3/4: Scanning source directory..." "White"
$scanResult = Scan-Source
if ($scanResult.Count -eq 0) {
    Write-Step "No files found in $Source — nothing to do." "Yellow"
    exit 0
}

# Step 4: Upload (or verify-only)
if ($VerifyOnly) {
    Write-Step "Step 4/4: VERIFY-ONLY mode" "Yellow"
    Write-Step "Skipping upload, running verification only..." "DarkGray"
    $copyExitCode = 0
    $checkExitCode = Invoke-RcloneCheck
}
else {
    Write-Step "Step 4/4: Uploading $(Format-Size $scanResult.Size) in $($scanResult.Count) files..." "White"
    $copyExitCode = Invoke-RcloneCopy

    # Verification
    if (-not $SkipVerification -and -not $DryRun) {
        $checkExitCode = Invoke-RcloneCheck
    }
    else {
        $checkExitCode = 0
        Write-Step "Verification skipped" "DarkGray"
    }
}

# Final report
$totalDuration = (Get-Date) - $Script:START_TIME
Show-FinalReport -ScanResult $scanResult -CopyExitCode $copyExitCode `
    -CheckExitCode $checkExitCode -TotalDuration $totalDuration

# Also save a clean text report
@"
======================================================================
R2 Archive Upload Report
======================================================================
Date:       $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Source:     $Source
Files:      $($scanResult.Count)
Total size: $(Format-Size $scanResult.Size)
Duration:   $(Format-Duration $totalDuration)
Exit codes: copy=$copyExitCode  check=$checkExitCode
======================================================================
"@ | Out-File -FilePath (Join-Path $PSScriptRoot "r2_upload_report.txt") -Encoding utf8

exit $copyExitCode
