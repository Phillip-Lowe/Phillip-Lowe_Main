#!/usr/bin/env python3
"""
SAOS Off-Site Backup Upload
Uploads encrypted backups to an S3-compatible storage.

Supports:
- AWS S3
- Cloudflare R2
- Backblaze B2
- Any S3-compatible endpoint

Environment Variables:
    SAOS_OFFSITE_S3_ENDPOINT    — S3 endpoint URL (e.g., https://s3.amazonaws.com)
    SAOS_OFFSITE_S3_BUCKET      — Bucket name
    SAOS_OFFSITE_S3_ACCESS_KEY  — Access key ID
    SAOS_OFFSITE_S3_SECRET_KEY  — Secret access key
    SAOS_OFFSITE_S3_REGION      — Region (default: us-east-1)
    SAOS_BACKUP_DIR             — Local backup directory (default: ~/saos-backups)

Usage:
    python3 offsite_backup.py                    # Upload latest backup
    python3 offsite_backup.py /path/to/file.enc  # Upload specific file
"""

import os
import sys
import boto3
from botocore.config import Config
from datetime import datetime, timezone
from pathlib import Path

def get_s3_client():
    endpoint = os.environ.get('SAOS_OFFSITE_S3_ENDPOINT')
    access_key = os.environ.get('SAOS_OFFSITE_S3_ACCESS_KEY')
    secret_key = os.environ.get('SAOS_OFFSITE_S3_SECRET_KEY')
    region = os.environ.get('SAOS_OFFSITE_S3_REGION', 'us-east-1')
    
    if not all([endpoint, access_key, secret_key]):
        missing = []
        if not endpoint: missing.append('SAOS_OFFSITE_S3_ENDPOINT')
        if not access_key: missing.append('SAOS_OFFSITE_S3_ACCESS_KEY')
        if not secret_key: missing.append('SAOS_OFFSITE_S3_SECRET_KEY')
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")
    
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    
    s3 = session.client(
        's3',
        endpoint_url=endpoint,
        config=Config(signature_version='s3v4')
    )
    
    return s3

def upload_backup(file_path, bucket=None):
    """Upload a backup file to off-site storage."""
    if not bucket:
        bucket = os.environ.get('SAOS_OFFSITE_S3_BUCKET')
    if not bucket:
        raise ValueError("SAOS_OFFSITE_S3_BUCKET not set")
    
    s3 = get_s3_client()
    file_name = os.path.basename(file_path)
    
    # Generate key with date prefix for organization
    date_prefix = datetime.now(timezone.utc).strftime('%Y/%m/%d')
    s3_key = f"saos-backups/{date_prefix}/{file_name}"
    
    print(f"Uploading: {file_path}")
    print(f"  Destination: s3://{bucket}/{s3_key}")
    
    # Upload with metadata
    extra_args = {
        'Metadata': {
            'uploaded_at': datetime.now(timezone.utc).isoformat(),
            'source': 'saos-backup-verify'
        }
    }
    
    try:
        s3.upload_file(file_path, bucket, s3_key, ExtraArgs=extra_args)
        print(f"  ✅ Upload successful")
        return s3_key
    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
        raise

def list_remote_backups(bucket=None, max_results=10):
    """List recent backups in off-site storage."""
    if not bucket:
        bucket = os.environ.get('SAOS_OFFSITE_S3_BUCKET')
    if not bucket:
        raise ValueError("SAOS_OFFSITE_S3_BUCKET not set")
    
    s3 = get_s3_client()
    
    try:
        response = s3.list_objects_v2(
            Bucket=bucket,
            Prefix='saos-backups/',
            MaxKeys=max_results
        )
        
        objects = response.get('Contents', [])
        print(f"Recent backups in s3://{bucket}/saos-backups/:")
        for obj in objects:
            size_mb = obj['Size'] / (1024 * 1024)
            print(f"  {obj['Key']} ({size_mb:.1f} MB, {obj['LastModified']})")
        return objects
    except Exception as e:
        print(f"Failed to list backups: {e}")
        return []

def main():
    import argparse
    parser = argparse.ArgumentParser(description="SAOS Off-Site Backup Upload")
    parser.add_argument("file", nargs="?", help="Specific file to upload")
    parser.add_argument("--list", action="store_true", help="List remote backups")
    parser.add_argument("--bucket", help="Override bucket name")
    args = parser.parse_args()
    
    if args.list:
        list_remote_backups(args.bucket)
        return
    
    if args.file:
        file_to_upload = args.file
        if not os.path.isfile(file_to_upload):
            print(f"❌ File not found: {file_to_upload}")
            sys.exit(1)
    else:
        # Find most recent backup
        backup_dir = os.environ.get('SAOS_BACKUP_DIR', os.path.expanduser('~/saos-backups'))
        backups = sorted(
            [f for f in os.listdir(backup_dir) if f.startswith('systack_memory_')],
            reverse=True
        )
        if not backups:
            print(f"❌ No backups found in {backup_dir}")
            sys.exit(1)
        file_to_upload = os.path.join(backup_dir, backups[0])
        print(f"Latest backup: {file_to_upload}")
    
    upload_backup(file_to_upload, args.bucket)

if __name__ == '__main__':
    main()
