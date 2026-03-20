"""
QuMail Controller
Orchestrates: key retrieval → encryption → email send
"""

from km_client.etsi_qkd_client import ETSIQKDClient
from security.encryption_engine import EncryptionEngine, OTPEngine
from security.policies import SecurityLevel
from email_client.smtp_client import SMTPClient
from email_client.secure_payload import SecurePayload


class QuMailController:

    def __init__(self):
        self.qkd_client = ETSIQKDClient()

    def send_secure_email(
        self,
        sender_email: str,
        app_password: str,
        recipient: str,
        subject: str,
        message: str,
        security_level: str = "QUANTUM_AES",
    ) -> dict:
        """
        Full secure send workflow:
        1. Fetch quantum key from KM
        2. Encrypt message
        3. Wrap in SecurePayload
        4. Send via SMTP
        """
        try:
            level = SecurityLevel(security_level)
        except ValueError:
            return {"success": False, "message": f"Unknown security level: {security_level}"}

        # ── Step 1: Get quantum key ──────────────────────────────────────────
        if level == SecurityLevel.NO_SECURITY:
            key_info = {"key_id": "none", "key_bytes": b"", "key_hex": ""}
        else:
            try:
                key_info = self.qkd_client.get_key()
            except Exception as e:
                return {"success": False, "message": f"Key Manager error: {str(e)}"}

        # ── Step 2: Encrypt ──────────────────────────────────────────────────
        try:
            if level == SecurityLevel.QUANTUM_AES:
                engine = EncryptionEngine()
                encrypted_data = engine.encrypt(message, key_info["key_bytes"])
            elif level == SecurityLevel.QUANTUM_OTP:
                key_bytes = key_info["key_bytes"]
                # OTP needs key as long as message; extend if needed
                msg_bytes = message.encode('utf-8')
                if len(key_bytes) < len(msg_bytes):
                    # Generate more key material
                    import os
                    key_bytes = key_bytes + os.urandom(len(msg_bytes) - len(key_bytes))
                    key_info["key_hex"] = key_bytes.hex()
                engine = OTPEngine()
                encrypted_data = engine.encrypt(message, key_bytes)
            elif level == SecurityLevel.PQC:
                # Use AES with quantum key (PQC simulation)
                engine = EncryptionEngine()
                encrypted_data = engine.encrypt(message, key_info["key_bytes"])
                encrypted_data["algorithm"] = "PQC-Kyber+AES-256-GCM (simulated)"
            else:  # NO_SECURITY
                encrypted_data = {"algorithm": "none", "plaintext": message}

        except Exception as e:
            return {"success": False, "message": f"Encryption error: {str(e)}"}

        # ── Step 3: Build payload ────────────────────────────────────────────
        email_body = SecurePayload.encode(
            encrypted_data=encrypted_data,
            key_id=key_info["key_id"],
            security_level=security_level,
            original_subject=subject,
        )
        full_subject = f"[QuMail Encrypted] {subject}"

        # ── Step 4: Send via SMTP ────────────────────────────────────────────
        smtp = SMTPClient(sender_email, app_password)
        result = smtp.send(recipient, full_subject, email_body)

        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "key_id": key_info["key_id"],
                "key_hex": key_info["key_hex"],
                "security_level": security_level,
                "algorithm": encrypted_data.get("algorithm", ""),
                "encrypted_preview": str(encrypted_data)[:100] + "...",
            }
        else:
            return result

    def km_status(self) -> dict:
        return self.qkd_client.status()
