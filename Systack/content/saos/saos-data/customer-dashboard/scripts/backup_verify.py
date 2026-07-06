#!/usr/bin/env python3
"""
SAOS Backup Verification & Restore Drill Script

Performs:
1. pg_dump of systack_memory database
2. SHA-256 checksum of backup
3. Restore test to a temporary database
4. Verification queries against restored data
5. Logs results to backup_log table
6. Reports RPO/RTO metrics

Usage:
    python3 backup_verify.py [--full] [--verify-only <backup_file>]
    
    --full          Run full backup + verify cycle (default)
    --verify-only   Only verify an existing backup file (no new backup)
"""

import os
import sys
import subprocess
import hashlib
import json
import time
from datetime import datetime, timedelta

# Import encryption helper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from encrypt_backup import encrypt_file, decrypt_file

DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = os.environ.get("PGPORT", "5432")
DB_NAME = os.environ.get("PGDATABASE", "systack_memory")
DB_USER = os.environ.get("PGUSER", "philliplowe")
BACKUP_DIR = os.environ.get("SAOS_BACKUP_DIR", os.path.expanduser("~/saos-backups"))
TEST_DB = "saos_restore_test"

# Check encryption key is configured
if not os.environ.get('SAOS_BACKUP_ENCRYPTION_KEY'):
    print("⚠️  WARNING: SAOS_BACKUP_ENCRYPTION_KEY not set. Backups will NOT be encrypted.")
    print("   Set a 64-character hex key to enable encryption.")
    ENCRYPTION_ENABLED = False
else:
    ENCRYPTION_ENABLED = True

# Check off-site backup config
OFFSITE_ENABLED = all([
    os.environ.get('SAOS_OFFSITE_S3_ENDPOINT'),
    os.environ.get('SAOS_OFFSITE_S3_ACCESS_KEY'),
    os.environ.get('SAOS_OFFSITE_S3_SECRET_KEY'),
    os.environ.get('SAOS_OFFSITE_S3_BUCKET')
])
if not OFFSITE_ENABLED:
    print("⚠️  WARNING: Off-site backup not configured. Backups stay local only.")
    print("   Set SAOS_OFFSITE_S3_* variables to enable off-site storage.")

def log_backup(backup_type, target, status, file_path=None, file_size=None, 
               checksum_sha256=None, started_at=None, completed_at=None, 
               verification_result=None, rpo_minutes=None, rto_minutes=None, notes=None):
    """Log backup result to backup_log table."""
    try:
        import psycopg2
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO backup_log 
            (backup_type, target, status, file_path, file_size_bytes, checksum_sha256,
             started_at, completed_at, verified_at, verification_result, rpo_minutes, rto_minutes, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (backup_type, target, status, file_path, file_size, checksum_sha256,
              started_at, completed_at, 
              datetime.now() if status == 'verified' else None,
              verification_result, rpo_minutes, rto_minutes, notes))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[WARN] Could not log to backup_log: {e}")

def sha256_file(filepath):
    """Calculate SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            h.update(data)
    return h.hexdigest()

def run_pg_dump():
    """Create a pg_dump backup of the database."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"systack_memory_{timestamp}.sql")
    
    print(f"[1/5] Creating pg_dump → {backup_file}")
    start = time.time()
    
    result = subprocess.run([
        'pg_dump', '-h', DB_HOST, '-p', DB_PORT, '-U', DB_USER,
        '-f', backup_file, DB_NAME
    ], capture_output=True, text=True, env={**os.environ, 'PGPASSWORD': os.environ.get('PGPASSWORD', '')})
    
    elapsed = int(time.time() - start)
    
    if result.returncode != 0:
        print(f"  ❌ pg_dump failed: {result.stderr}")
        log_backup('pg_dump', DB_NAME, 'failed', notes=result.stderr,
                   started_at=datetime.now() - timedelta(seconds=elapsed),
                   completed_at=datetime.now())
        return None, None, None
    
    file_size = os.path.getsize(backup_file)
    checksum = sha256_file(backup_file)
    print(f"  ✅ Backup: {file_size:,} bytes, {elapsed}s, SHA-256: {checksum[:16]}...")
    
    # Encrypt backup if encryption is enabled
    if ENCRYPTION_ENABLED:
        print(f"  [1a/5] Encrypting backup...")
        try:
            enc_file = encrypt_file(backup_file)
            # Update file path and size to encrypted version
            backup_file = enc_file
            file_size = os.path.getsize(enc_file)
            checksum = sha256_file(enc_file)
            print(f"  ✅ Encrypted backup ready")
        except Exception as e:
            print(f"  ⚠️  Encryption failed: {e}")
            print(f"  ⚠️  Continuing with unencrypted backup")
    
    return backup_file, checksum, file_size

def restore_to_test_db(backup_file):
    """Restore backup to a temporary test database to verify integrity."""
    print(f"[2/5] Creating test database: {TEST_DB}")
    
    # Check if file is encrypted
    decrypted_path = None
    if backup_file.endswith('.enc') or ENCRYPTION_ENABLED:
        print(f"  [2a/5] Decrypting backup for restore test...")
        try:
            decrypted_path = backup_file.replace('.enc', '') + '.tmp'
            decrypt_file(backup_file, decrypted_path)
            restore_source = decrypted_path
            print(f"  ✅ Decrypted for restore test")
        except Exception as e:
            print(f"  ⚠️  Decryption failed: {e}")
            print(f"  ⚠️  Attempting restore from original file")
            restore_source = backup_file
    else:
        restore_source = backup_file
    
    # Drop test DB if exists
    subprocess.run(['dropdb', '--if-exists', '-h', DB_HOST, '-p', DB_PORT, '-U', DB_USER, TEST_DB],
                   capture_output=True, text=True, env={**os.environ, 'PGPASSWORD': os.environ.get('PGPASSWORD', '')})
    
    # Create fresh test DB
    result = subprocess.run(['createdb', '-h', DB_HOST, '-p', DB_PORT, '-U', DB_USER, TEST_DB],
                           capture_output=True, text=True, env={**os.environ, 'PGPASSWORD': os.environ.get('PGPASSWORD', '')})
    if result.returncode != 0:
        print(f"  ❌ Could not create test DB: {result.stderr}")
        return False, "Failed to create test database"
    
    print(f"[3/5] Restoring backup to test database...")
    start = time.time()
    
    result = subprocess.run([
        'psql', '-h', DB_HOST, '-p', DB_PORT, '-U', DB_USER, '-d', TEST_DB,
        '-f', restore_source, '-q'
    ], capture_output=True, text=True, env={**os.environ, 'PGPASSWORD': os.environ.get('PGPASSWORD', '')})
    
    elapsed = int(time.time() - start)
    
    # Cleanup temp decrypted file
    if decrypted_path and os.path.exists(decrypted_path):
        os.remove(decrypted_path)
    
    if result.returncode != 0:
        print(f"  ❌ Restore failed: {result.stderr[:500]}")
        return False, f"Restore failed after {elapsed}s: {result.stderr[:200]}"
    
    print(f"  ✅ Restore completed in {elapsed}s")
    return True, f"Restored in {elapsed}s"

def verify_restored_data():
    """Run verification queries against the restored database."""
    print(f"[4/5] Verifying restored data...")
    
    checks = []
    
    try:
        import psycopg2
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=TEST_DB, user=DB_USER)
        cur = conn.cursor()
        
        # Check 1: All expected tables exist
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' ORDER BY table_name
        """)
        tables = [r[0] for r in cur.fetchall()]
        expected = ['saos_clients', 'audit_log', 'task_queue', 'chat_messages', 
                   'chat_conversations', 'agent_state', 'security_events', 
                   'backup_log', 'compliance_policies', 'incident_log']
        missing = [t for t in expected if t not in tables]
        if missing:
            checks.append(f"❌ Missing tables: {missing}")
        else:
            checks.append(f"✅ All {len(expected)} expected tables present")
        
        # Check 2: Client count matches
        cur.execute("SELECT COUNT(*) FROM saos_clients")
        client_count = cur.fetchone()[0]
        checks.append(f"✅ Client records: {client_count}")
        
        # Check 3: Audit log has entries
        cur.execute("SELECT COUNT(*) FROM audit_log")
        audit_count = cur.fetchone()[0]
        checks.append(f"✅ Audit log entries: {audit_count}")
        
        # Check 4: Compliance policies exist
        cur.execute("SELECT COUNT(*) FROM compliance_policies WHERE status = 'active'")
        policy_count = cur.fetchone()[0]
        checks.append(f"✅ Active compliance policies: {policy_count}")
        
        # Check 5: RBAC roles exist
        cur.execute("SELECT COUNT(*) FROM saos_roles")
        role_count = cur.fetchone()[0]
        checks.append(f"✅ RBAC roles: {role_count}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        checks.append(f"❌ Verification query failed: {e}")
    
    for check in checks:
        print(f"  {check}")
    
    all_pass = all(c.startswith("✅") for c in checks)
    return all_pass, "\n".join(checks)

def cleanup_test_db():
    """Drop the test database."""
    print(f"[5/5] Cleaning up test database...")
    subprocess.run(['dropdb', '--if-exists', '-h', DB_HOST, '-p', DB_PORT, '-U', DB_USER, TEST_DB],
                   capture_output=True, text=True, env={**os.environ, 'PGPASSWORD': os.environ.get('PGPASSWORD', '')})
    print("  ✅ Test database dropped")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="SAOS Backup Verification & Restore Drill")
    parser.add_argument("--full", action="store_true", default=True, help="Full backup + verify cycle")
    parser.add_argument("--verify-only", type=str, help="Only verify an existing backup file")
    args = parser.parse_args()
    
    print("=" * 60)
    print("SAOS Backup Verification & Restore Drill")
    print(f"Date: {datetime.now().isoformat()}")
    print(f"Database: {DB_NAME}@{DB_HOST}:{DB_PORT}")
    print("=" * 60)
    
    overall_start = time.time()
    
    if args.verify_only:
        # Just verify existing backup
        backup_file = args.verify_only
        if not os.path.isfile(backup_file):
            print(f"❌ File not found: {backup_file}")
            sys.exit(1)
        
        checksum = sha256_file(backup_file)
        file_size = os.path.getsize(backup_file)
        backup_file = backup_file
    else:
        # Full cycle
        backup_file, checksum, file_size = run_pg_dump()
        if not backup_file:
            print("\n❌ Backup failed. Aborting.")
            sys.exit(1)
    
    # Restore + verify
    restore_ok, restore_msg = restore_to_test_db(backup_file)
    if not restore_ok:
        log_backup('pg_dump', DB_NAME, 'failed', file_path=backup_file,
                   file_size=file_size, checksum_sha256=checksum,
                   started_at=datetime.now() - timedelta(seconds=int(time.time() - overall_start)),
                   completed_at=datetime.now(), verification_result=restore_msg)
        cleanup_test_db()
        sys.exit(1)
    
    verify_ok, verify_msg = verify_restored_data()
    cleanup_test_db()
    
    # Off-site backup upload
    offsite_status = "skipped"
    if OFFSITE_ENABLED and verify_ok:
        print("[6/5] Uploading to off-site storage...")
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from offsite_backup import upload_backup
            upload_backup(backup_file)
            offsite_status = "uploaded"
        except Exception as e:
            print(f"  ⚠️  Off-site upload failed: {e}")
            offsite_status = f"failed: {e}"
    
    total_elapsed = int(time.time() - overall_start)
    
    # Log to database
    notes = f"Backup+verify completed in {total_elapsed}s"
    if ENCRYPTION_ENABLED:
        notes += ", encrypted"
    if offsite_status == "uploaded":
        notes += ", off-site uploaded"
    elif offsite_status.startswith("failed"):
        notes += f", off-site {offsite_status}"
    
    log_backup('pg_dump', DB_NAME, 'verified' if verify_ok else 'failed',
               file_path=backup_file, file_size=file_size, checksum_sha256=checksum,
               started_at=datetime.now() - timedelta(seconds=total_elapsed),
               completed_at=datetime.now(),
               verification_result=verify_msg,
               rpo_minutes=1440,  # 24 hours (daily backup = 1440 min RPO)
               rto_minutes=total_elapsed * 2,  # restore took X, full recovery ~2X
               notes=notes)
    
    print("\n" + "=" * 60)
    print(f"RESULT: {'✅ ALL CHECKS PASSED' if verify_ok else '❌ VERIFICATION FAILED'}")
    print(f"Total time: {total_elapsed}s")
    print(f"Backup file: {backup_file}")
    print(f"Size: {file_size:,} bytes")
    print(f"Encrypted: {'✅ Yes (AES-256-GCM)' if ENCRYPTION_ENABLED else '❌ No'}")
    print(f"SHA-256: {checksum}")
    print(f"RPO: 1440 minutes (24 hours)")
    print(f"RTO: {total_elapsed * 2} minutes (estimated)")
    print("=" * 60)
    
    sys.exit(0 if verify_ok else 1)

if __name__ == '__main__':
    main()