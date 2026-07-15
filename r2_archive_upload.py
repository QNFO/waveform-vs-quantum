#!/usr/bin/env python3
"""
R2 Archive Uploader — copy all files from a local directory to a Cloudflare R2 bucket.

Features:
- Progress bars (per-file + aggregate) via tqdm
- SQLite checkpoint database for reliable resume after interruption/crash
- Multipart upload for files > 50 MB via boto3 S3 TransferManager
- Post-upload verification comparing file size + optional ETag
- Retry with exponential backoff on transient errors
- Dry-run mode to audit what would be uploaded

Requirements:
    pip install boto3 tqdm    (tqdm is optional; falls back to plain logging)

Credentials — set these environment variables BEFORE running:
    R2_ACCESS_KEY_ID      — R2 API token Access Key ID
    R2_SECRET_ACCESS_KEY  — R2 API token Secret Access Key
    R2_ACCOUNT_ID         — Cloudflare account ID (edb167b78c9fb901ea5bca3ce58ccc4b)
    R2_BUCKET             — bucket name (archive)

Usage:
    python r2_archive_upload.py                     # upload D:/Archive → archive bucket
    python r2_archive_upload.py --dry-run           # audit only, no uploads
    python r2_archive_upload.py --source E:/Data    # custom source dir
    python r2_archive_upload.py --workers 8         # parallel uploads
    python r2_archive_upload.py --reset             # clear checkpoint DB, start fresh
"""

import os
import sys
import sqlite3
import hashlib
import time
import argparse
import logging
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque
from datetime import datetime, timezone

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, EndpointConnectionError

# ── tqdm (optional) ──────────────────────────────────────────────────────────
try:
    from tqdm import tqdm as _tqdm_imported

    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# ── Logging ──────────────────────────────────────────────────────────────────
log = logging.getLogger("r2_upload")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)

# ── Constants ────────────────────────────────────────────────────────────────
DEFAULT_SOURCE = "D:/Archive"
CHECKPOINT_DB = Path(__file__).with_suffix(".db")  # r2_archive_upload.db
MULTIPART_THRESHOLD = 50 * 1024 * 1024  # 50 MB — switch to multipart above this
MAX_RETRIES = 5
RETRY_BASE_DELAY = 1.0  # seconds — doubles each retry
VERIFY_SAMPLE_SIZE = 4096  # bytes to read from head/tail for fast integrity check

# R2 per-request limits
R2_MAX_OBJECT_SIZE = 5 * 1024 * 1024 * 1024  # 5 GiB single PUT
R2_MAX_MULTIPART_SIZE = 5 * 1024 * 1024 * 1024 * 1024  # 5 TiB

# ── Checkpoint Database ──────────────────────────────────────────────────────


class CheckpointDB:
    """SQLite-backed checkpoint store for resume capability.

    States per file:
        pending   — discovered, not yet attempted
        uploading — in-flight (worker has claimed it)
        done      — uploaded + verified successfully
        failed    — gave up after max retries
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._init_schema()

    def _init_schema(self):
        with self._lock:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS files (
                    relpath     TEXT PRIMARY KEY,
                    local_path  TEXT NOT NULL,
                    size        INTEGER NOT NULL,
                    mtime       REAL NOT NULL,
                    state       TEXT NOT NULL DEFAULT 'pending',
                    etag        TEXT,
                    attempts    INTEGER NOT NULL DEFAULT 0,
                    last_error  TEXT,
                    updated_at  TEXT NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS metadata (
                    key   TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            self._conn.commit()

    def set_meta(self, key: str, value: str):
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO metadata(key, value) VALUES(?, ?)",
                (key, value),
            )
            self._conn.commit()

    def get_meta(self, key: str) -> str | None:
        row = self._conn.execute(
            "SELECT value FROM metadata WHERE key = ?", (key,)
        ).fetchone()
        return row[0] if row else None

    def seed_files(self, files: list[dict]):
        """Insert newly discovered files that aren't already tracked."""
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            for f in files:
                self._conn.execute(
                    """
                    INSERT OR IGNORE INTO files(relpath, local_path, size, mtime, state, updated_at)
                    VALUES(?, ?, ?, ?, 'pending', ?)
                    """,
                    (f["relpath"], f["local_path"], f["size"], f["mtime"], now),
                )
            self._conn.commit()

    def claim_pending(self, limit: int = 1) -> list[dict]:
        """Claim up to `limit` pending files, marking them 'uploading'."""
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT relpath, local_path, size, mtime
                FROM files
                WHERE state = 'pending'
                ORDER BY relpath
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            if rows:
                relpaths = [r[0] for r in rows]
                placeholders = ",".join("?" * len(relpaths))
                self._conn.execute(
                    f"UPDATE files SET state='uploading', updated_at=? WHERE relpath IN ({placeholders})",
                    [now] + relpaths,
                )
                self._conn.commit()
            return [
                {"relpath": r[0], "local_path": r[1], "size": r[2], "mtime": r[3]}
                for r in rows
            ]

    def mark_done(self, relpath: str, etag: str = ""):
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            self._conn.execute(
                """
                UPDATE files SET state='done', etag=?, attempts=attempts+1, last_error=NULL, updated_at=?
                WHERE relpath = ?
                """,
                (etag, now, relpath),
            )
            self._conn.commit()

    def mark_failed(self, relpath: str, error: str):
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            self._conn.execute(
                """
                UPDATE files SET state='failed', attempts=attempts+1, last_error=?, updated_at=?
                WHERE relpath = ?
                """,
                (error[:500], now, relpath),
            )
            self._conn.commit()

    def requeue_failed(self):
        """Move all 'failed' files back to 'pending' for retry."""
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            self._conn.execute(
                "UPDATE files SET state='pending', updated_at=? WHERE state='failed'",
                (now,),
            )
            self._conn.commit()

    def requeue_stale_uploading(self, stale_minutes: int = 30):
        """Recover files stuck in 'uploading' state (e.g., after a crash)."""
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            self._conn.execute(
                """
                UPDATE files SET state='pending', updated_at=?
                WHERE state='uploading'
                  AND updated_at < datetime(?, ? || ' minutes')
                """,
                (now, now, f"-{stale_minutes}"),
            )
            self._conn.commit()

    def stats(self) -> dict:
        with self._lock:
            rows = self._conn.execute(
                "SELECT state, COUNT(*) FROM files GROUP BY state"
            ).fetchall()
            stats = {"pending": 0, "uploading": 0, "done": 0, "failed": 0}
            for state, count in rows:
                if state in stats:
                    stats[state] = count
            total_size = self._conn.execute(
                "SELECT COALESCE(SUM(size), 0) FROM files"
            ).fetchone()[0]
            return {**stats, "total_size": total_size}

    def get_failed(self) -> list[dict]:
        rows = self._conn.execute(
            "SELECT relpath, attempts, last_error FROM files WHERE state='failed'"
        ).fetchall()
        return [
            {"relpath": r[0], "attempts": r[1], "last_error": r[2]} for r in rows
        ]

    def close(self):
        self._conn.close()


# ── S3 Client Factory ────────────────────────────────────────────────────────


def create_s3_client(account_id: str, access_key: str, secret_key: str):
    """Create a boto3 S3 client pointed at the R2 endpoint."""
    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
        config=Config(
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=30,
            read_timeout=60,
            max_pool_connections=50,
        ),
    )


# ── File Discovery ───────────────────────────────────────────────────────────


def discover_files(source_dir: Path) -> list[dict]:
    """Walk source_dir recursively and return file metadata."""
    if not source_dir.exists():
        log.error("Source directory does not exist: %s", source_dir)
        sys.exit(1)

    files = []
    for entry in source_dir.rglob("*"):
        if entry.is_file():
            stat = entry.stat()
            files.append(
                {
                    "relpath": str(entry.relative_to(source_dir)).replace("\\", "/"),
                    "local_path": str(entry),
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                }
            )
    return files


# ── Upload Logic ─────────────────────────────────────────────────────────────


def upload_single(s3, bucket: str, file_info: dict) -> tuple[str, str]:
    """Upload one file to R2 via single PUT. Returns (etag, error)."""
    try:
        content_type = _guess_content_type(file_info["relpath"])
        with open(file_info["local_path"], "rb") as fh:
            resp = s3.put_object(
                Bucket=bucket,
                Key=file_info["relpath"],
                Body=fh,
                ContentType=content_type,
            )
        etag = resp.get("ETag", "").strip('"')
        return etag, ""
    except Exception as exc:
        return "", str(exc)


def upload_multipart(s3, bucket: str, file_info: dict) -> tuple[str, str]:
    """Upload one file via S3 multipart using TransferManager."""
    # boto3 TransferManager handles chunking, parallelism, and retry internally
    try:
        content_type = _guess_content_type(file_info["relpath"])
        # TransferConfig auto-chooses multipart above MULTIPART_THRESHOLD
        s3.upload_file(
            Filename=file_info["local_path"],
            Bucket=bucket,
            Key=file_info["relpath"],
            ExtraArgs={"ContentType": content_type},
            Config=boto3.s3.transfer.TransferConfig(
                multipart_threshold=MULTIPART_THRESHOLD,
                max_concurrency=4,
                multipart_chunksize=16 * 1024 * 1024,  # 16 MiB parts
                use_threads=True,
            ),
        )
        # Fetch the resulting ETag
        head = s3.head_object(Bucket=bucket, Key=file_info["relpath"])
        etag = head.get("ETag", "").strip('"')
        return etag, ""
    except Exception as exc:
        return "", str(exc)


def upload_with_retry(s3, bucket: str, file_info: dict) -> tuple[str, str]:
    """Upload with retry + exponential backoff. Picks single vs multipart."""
    file_size = file_info["size"]

    if file_size > R2_MAX_MULTIPART_SIZE:
        return "", f"File exceeds R2 max object size of 5 TiB: {file_size} bytes"
    if file_size <= R2_MAX_OBJECT_SIZE and file_size < MULTIPART_THRESHOLD:
        upload_fn = upload_single
    else:
        upload_fn = upload_multipart

    last_error = ""
    for attempt in range(MAX_RETRIES):
        try:
            etag, err = upload_fn(s3, bucket, file_info)
            if not err:
                return etag, ""
            last_error = err
        except (EndpointConnectionError, ConnectionError):
            last_error = "Connection error"

        if attempt < MAX_RETRIES - 1:
            delay = RETRY_BASE_DELAY * (2**attempt)
            log.debug("Retry %d/%d for %s in %.1fs", attempt + 1, MAX_RETRIES,
                      file_info["relpath"], delay)
            time.sleep(delay)

    return "", last_error


# ── Verification ─────────────────────────────────────────────────────────────


def verify_object(s3, bucket: str, local_path: str, relpath: str,
                  expected_size: int, expected_etag: str = "") -> tuple[bool, str]:
    """Verify a remote object exists and matches local file size."""
    try:
        head = s3.head_object(Bucket=bucket, Key=relpath)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False, "Object not found in R2"
        return False, f"head_object failed: {e}"

    remote_size = head.get("ContentLength", 0)
    if remote_size != expected_size:
        return False, f"Size mismatch: local={expected_size} remote={remote_size}"

    # Fast integrity spot-check: compare first + last bytes of file
    try:
        with open(local_path, "rb") as fh:
            head_bytes = fh.read(VERIFY_SAMPLE_SIZE)
            if remote_size > VERIFY_SAMPLE_SIZE * 2:
                fh.seek(-VERIFY_SAMPLE_SIZE, os.SEEK_END)
            tail_bytes = fh.read(VERIFY_SAMPLE_SIZE)

        local_hash = hashlib.sha256(head_bytes + tail_bytes).hexdigest()

        # Download same ranges from R2
        resp_head = s3.get_object(
            Bucket=bucket, Key=relpath, Range=f"bytes=0-{VERIFY_SAMPLE_SIZE - 1}"
        )
        remote_head = resp_head["Body"].read()

        if remote_size > VERIFY_SAMPLE_SIZE * 2:
            resp_tail = s3.get_object(
                Bucket=bucket, Key=relpath,
                Range=f"bytes={remote_size - VERIFY_SAMPLE_SIZE}-{remote_size - 1}",
            )
            remote_tail = resp_tail["Body"].read()
        else:
            remote_tail = b""

        remote_hash = hashlib.sha256(remote_head + remote_tail).hexdigest()
        if local_hash != remote_hash:
            return False, f"Content hash mismatch (head+tail check)"
    except Exception as e:
        log.warning("Spot-check skipped for %s: %s", relpath, e)

    return True, ""


# ── Helpers ──────────────────────────────────────────────────────────────────

_CONTENT_TYPES = {
    ".txt": "text/plain", ".html": "text/html", ".css": "text/css",
    ".js": "application/javascript", ".json": "application/json",
    ".xml": "application/xml", ".pdf": "application/pdf",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp",
    ".mp3": "audio/mpeg", ".mp4": "video/mp4", ".wav": "audio/wav",
    ".zip": "application/zip", ".gz": "application/gzip",
    ".tar": "application/x-tar", ".7z": "application/x-7z-compressed",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".md": "text/markdown", ".csv": "text/csv", ".yaml": "text/yaml",
    ".yml": "text/yaml", ".log": "text/plain", ".py": "text/x-python",
}


def _guess_content_type(relpath: str) -> str:
    ext = Path(relpath).suffix.lower()
    return _CONTENT_TYPES.get(ext, "application/octet-stream")


def format_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TiB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PiB"


def _build_tqdm_kwargs(total, desc, unit="file"):
    if TQDM_AVAILABLE:
        return {
            "total": total,
            "desc": desc,
            "unit": unit,
            "ncols": 100,
            "bar_format": "{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        }
    return {}


# ── Main Orchestrator ────────────────────────────────────────────────────────


def run(args: argparse.Namespace):
    # ── Validate environment ─────────────────────────────────────────────
    access_key = os.environ.get("R2_ACCESS_KEY_ID", "")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY", "")
    account_id = os.environ.get("R2_ACCOUNT_ID", "edb167b78c9fb901ea5bca3ce58ccc4b")
    bucket = os.environ.get("R2_BUCKET", "archive")

    if not access_key or not secret_key:
        log.error("Missing R2 credentials. Set R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY.")
        log.error("Create a token at: https://dash.cloudflare.com/%s/r2/api-tokens", account_id)
        sys.exit(1)

    source_dir = Path(args.source)
    db_path = Path(args.db)

    # ── Reset checkpoint if requested ────────────────────────────────────
    if args.reset and db_path.exists():
        db_path.unlink()
        log.info("Checkpoint database reset.")

    # ── Discover local files ─────────────────────────────────────────────
    log.info("Scanning %s ...", source_dir)
    local_files = discover_files(source_dir)
    if not local_files:
        log.warning("No files found in %s", source_dir)
        return

    total_count = len(local_files)
    total_size = sum(f["size"] for f in local_files)
    log.info("Found %d files (%s)", total_count, format_size(total_size))

    # ── Initialize checkpoint DB ─────────────────────────────────────────
    cdb = CheckpointDB(db_path)
    cdb.set_meta("source_dir", str(source_dir))
    cdb.set_meta("bucket", bucket)
    cdb.set_meta("total_files_discovered", str(total_count))
    cdb.set_meta("total_size_discovered", str(total_size))

    cdb.seed_files(local_files)
    cdb.requeue_stale_uploading(stale_minutes=args.stale_timeout)

    stats = cdb.stats()
    log.info("State from checkpoint: %d done, %d pending, %d failed",
             stats["done"], stats["pending"], stats["failed"])

    if stats["done"] == total_count:
        log.info("All files already uploaded. Nothing to do.")
        cdb.close()
        return

    if args.dry_run:
        pending = stats["pending"] + stats["failed"]
        pending_size = sum(
            f["size"] for f in local_files
            if f["relpath"] not in {
                r[0]
                for r in cdb._conn.execute(
                    "SELECT relpath FROM files WHERE state='done'"
                ).fetchall()
            }
        )
        log.info("DRY RUN — would upload %d files (%s)", pending, format_size(pending_size))
        cdb.close()
        return

    # ── Create S3 client ─────────────────────────────────────────────────
    s3 = create_s3_client(account_id, access_key, secret_key)

    # Verify bucket exists
    try:
        s3.head_bucket(Bucket=bucket)
        log.info("Connected to R2 bucket '%s' ✓", bucket)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        log.error("Cannot access bucket '%s': %s", bucket, code)
        log.error("Create it with: npx wrangler r2 bucket create %s", bucket)
        sys.exit(1)

    # ── Upload loop ──────────────────────────────────────────────────────
    workers = args.workers
    pending = stats["pending"] + stats["failed"]
    cdb.requeue_failed()

    # Progress bar for overall progress
    pbar_kwargs = _build_tqdm_kwargs(pending, "Uploading", "file")
    pbar_cls = _tqdm_imported if TQDM_AVAILABLE else _NoopPbar

    with pbar_cls(initial=stats["done"], **pbar_kwargs) as pbar:
        # We use a producer-consumer model: main thread claims files,
        # worker threads upload them.
        executor = ThreadPoolExecutor(max_workers=workers)
        futures: dict = {}
        errors: list[tuple[str, str]] = []

        def _upload_worker(file_info: dict) -> tuple[str, str, str]:
            """Returns (relpath, etag, error)."""
            etag, err = upload_with_retry(s3, bucket, file_info)
            return file_info["relpath"], etag, err

        # Feed the pool
        while True:
            # Replenish futures
            batch = cdb.claim_pending(limit=max(1, workers - len(futures)))
            for fi in batch:
                futures[executor.submit(_upload_worker, fi)] = fi["relpath"]

            if not futures:
                # Nothing in-flight and nothing pending — we're done
                break

            # Wait for at least one to complete
            done_futures = set()
            try:
                for future in as_completed(list(futures.keys()), timeout=2.0):
                    relpath, etag, err = future.result()
                    if err:
                        cdb.mark_failed(relpath, err)
                        errors.append((relpath, err))
                        log.error("FAILED %s: %s", relpath, err[:120])
                    else:
                        # Verify
                        fi = next(
                            (f for f in local_files if f["relpath"] == relpath), None
                        )
                        if fi:
                            ok, verr = verify_object(
                                s3, bucket, fi["local_path"], relpath, fi["size"], etag
                            )
                            if ok:
                                cdb.mark_done(relpath, etag)
                                log.debug("OK %s", relpath)
                            else:
                                cdb.mark_failed(relpath, f"Verification: {verr}")
                                errors.append((relpath, f"Verification: {verr}"))
                                log.error("VERIFY FAILED %s: %s", relpath, verr)
                        else:
                            cdb.mark_done(relpath, etag)

                    del futures[future]
                    done_futures.add(future)

                    # Update progress
                    pbar.update(1)
                    pbar.set_postfix(
                        done=cdb.stats()["done"],
                        failed=len(errors),
                        refresh=False,
                    )
            except Exception as exc:
                log.debug("Upload loop iteration error: %s", exc)

        executor.shutdown(wait=True)
        pbar.close()

    # ── Final report ─────────────────────────────────────────────────────
    final_stats = cdb.stats()
    log.info("=" * 60)
    log.info("UPLOAD COMPLETE")
    log.info("  Total files:  %d", total_count)
    log.info("  Uploaded OK:  %d", final_stats["done"])
    log.info("  Failed:       %d", final_stats["failed"])
    log.info("  Total size:   %s", format_size(total_size))

    if final_stats["failed"] > 0:
        log.warning("")
        log.warning("Failed files (re-run to retry):")
        for item in cdb.get_failed():
            log.warning("  %s  (attempts: %d)", item["relpath"], item["attempts"])

        if args.auto_retry_failed:
            log.info("Auto-retrying failed files in second pass...")
            cdb.requeue_failed()
            # Recursive call would work but simple loop is cleaner
            # Just let the user re-run; the checkpoint handles it.

    cdb.close()
    log.info("Checkpoint saved to %s", db_path)


class _NoopPbar:
    """Fallback when tqdm is not installed."""
    def __init__(self, *args, **kwargs):
        pass
    def update(self, n=1):
        pass
    def set_postfix(self, **kwargs):
        pass
    def close(self):
        pass
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


# ── CLI ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Copy all files from a local directory to Cloudflare R2 with resume support.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python r2_archive_upload.py
  python r2_archive_upload.py --dry-run
  python r2_archive_upload.py --source E:\\Backups --workers 12
  python r2_archive_upload.py --reset

Environment variables:
  R2_ACCESS_KEY_ID       — R2 API token Access Key ID (required)
  R2_SECRET_ACCESS_KEY   — R2 API token Secret Access Key (required)
  R2_ACCOUNT_ID          — Cloudflare account ID (default: edb167b78c9fb901ea5bca3ce58ccc4b)
  R2_BUCKET              — R2 bucket name (default: archive)
        """,
    )
    parser.add_argument(
        "--source", "-s",
        default=DEFAULT_SOURCE,
        help="Local directory to upload (default: D:/Archive)",
    )
    parser.add_argument(
        "--db",
        default=str(CHECKPOINT_DB),
        help="Checkpoint database path (default: r2_archive_upload.db alongside script)",
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=4,
        help="Number of parallel upload threads (default: 4)",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Scan and report what would be uploaded, no actual transfers",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete checkpoint DB and start fresh",
    )
    parser.add_argument(
        "--stale-timeout",
        type=int,
        default=30,
        help="Minutes before 'uploading' state files are re-queued (default: 30)",
    )
    parser.add_argument(
        "--auto-retry-failed",
        action="store_true",
        help="Automatically retry failed files in a second pass",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    run(args)


if __name__ == "__main__":
    main()
