#!/usr/bin/env python3
"""
SAOS Backup Encryption Script
Encrypts PostgreSQL backups using AES-256-GCM with a key from environment.

Usage:
    python3 encrypt_backup.py /path/to/backup.sql [output_path]

Environment:
    SAOS_BACKUP_ENCRYPTION_KEY — hex-encoded 32-byte key (64 hex chars)
"""

import os
import sys
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets

def get_key():
    key_hex = os.environ.get('SAOS_BACKUP_ENCRYPTION_KEY')
    if not key_hex:
        raise ValueError("SAOS_BACKUP_ENCRYPTION_KEY environment variable not set")
    if len(key_hex) != 64:
        raise ValueError("SAOS_BACKUP_ENCRYPTION_KEY must be 64 hex characters (32 bytes)")
    return bytes.fromhex(key_hex)

def encrypt_file(input_path, output_path=None):
    key = get_key()
    
    # Read input
    with open(input_path, 'rb') as f:
        plaintext = f.read()
    
    # Generate nonce (96 bits for GCM)
    nonce = secrets.token_bytes(12)
    
    # Encrypt
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    
    # Output: nonce + ciphertext
    if not output_path:
        output_path = input_path + '.enc'
    
    with open(output_path, 'wb') as f:
        f.write(nonce + ciphertext)
    
    # Verify by decrypting
    aesgcm_check = AESGCM(key)
    decrypted = aesgcm_check.decrypt(nonce, ciphertext, None)
    if decrypted != plaintext:
        raise ValueError("Verification failed: decrypted data does not match original")
    
    # Calculate checksums
    orig_hash = hashlib.sha256(plaintext).hexdigest()[:16]
    enc_hash = hashlib.sha256(open(output_path, 'rb').read()).hexdigest()[:16]
    
    print(f"Encrypted: {input_path}")
    print(f"Output: {output_path}")
    print(f"Original SHA-256: {orig_hash}...")
    print(f"Encrypted SHA-256: {enc_hash}...")
    print(f"Size: {len(plaintext)} bytes → {len(nonce) + len(ciphertext)} bytes")
    print("Verification: PASS")
    
    return output_path

def decrypt_file(input_path, output_path=None):
    key = get_key()
    
    with open(input_path, 'rb') as f:
        data = f.read()
    
    nonce = data[:12]
    ciphertext = data[12:]
    
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    
    if not output_path:
        output_path = input_path.replace('.enc', '') + '.decrypted'
    
    with open(output_path, 'wb') as f:
        f.write(plaintext)
    
    print(f"Decrypted: {input_path}")
    print(f"Output: {output_path}")
    return output_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 encrypt_backup.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    encrypt_file(input_file, output_file)
