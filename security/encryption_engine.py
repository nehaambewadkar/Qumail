"""AES-256-GCM Encryption Engine for QuMail"""

import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class EncryptionEngine:
    """Handles AES-256-GCM encryption and decryption"""

    def encrypt(self, plaintext: str, key: bytes) -> dict:
        """
        Encrypt plaintext using AES-256-GCM.
        Returns a dict with nonce, ciphertext, tag (all base64 encoded).
        """
        if len(key) != 32:
            raise ValueError(f"Key must be 32 bytes (256-bit), got {len(key)}")

        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        plaintext_bytes = plaintext.encode('utf-8')

        # AESGCM.encrypt returns ciphertext + tag (tag is last 16 bytes)
        ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext_bytes, None)

        return {
            "algorithm": "AES-256-GCM",
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "ciphertext": base64.b64encode(ciphertext_with_tag[:-16]).decode('utf-8'),
            "tag": base64.b64encode(ciphertext_with_tag[-16:]).decode('utf-8'),
        }

    def decrypt(self, encrypted_data: dict, key: bytes) -> str:
        """
        Decrypt AES-256-GCM encrypted data.
        encrypted_data must have nonce, ciphertext, tag (base64 encoded).
        """
        if len(key) != 32:
            raise ValueError(f"Key must be 32 bytes (256-bit), got {len(key)}")

        aesgcm = AESGCM(key)
        nonce = base64.b64decode(encrypted_data["nonce"])
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        tag = base64.b64decode(encrypted_data["tag"])

        ciphertext_with_tag = ciphertext + tag
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
        return plaintext_bytes.decode('utf-8')


class OTPEngine:
    """One-Time Pad encryption (XOR with key)"""

    def encrypt(self, plaintext: str, key: bytes) -> dict:
        plaintext_bytes = plaintext.encode('utf-8')
        if len(key) < len(plaintext_bytes):
            raise ValueError("OTP key must be at least as long as plaintext")
        ciphertext = bytes(a ^ b for a, b in zip(plaintext_bytes, key[:len(plaintext_bytes)]))
        return {
            "algorithm": "OTP",
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "length": len(plaintext_bytes),
        }

    def decrypt(self, encrypted_data: dict, key: bytes) -> str:
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        plaintext_bytes = bytes(a ^ b for a, b in zip(ciphertext, key[:len(ciphertext)]))
        return plaintext_bytes.decode('utf-8')
