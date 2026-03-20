"""IMAP Client for receiving and decrypting emails from Gmail"""

import imaplib
import email
import ssl
from email.header import decode_header
from config.settings import IMAP_SERVER, IMAP_PORT
from email_client.secure_payload import SecurePayload


class IMAPClient:
    """Fetch emails via Gmail IMAP with SSL"""

    def __init__(self, email_addr: str, app_password: str):
        self.email_addr = email_addr
        self.password = app_password

    def _connect(self):
        context = ssl.create_default_context()
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context)
        mail.login(self.email_addr, self.password)
        return mail

    def fetch_inbox(self, limit: int = 10) -> list:
        """Fetch recent emails from inbox"""
        try:
            mail = self._connect()
            mail.select("INBOX")
            _, message_ids = mail.search(None, "ALL")
            ids = message_ids[0].split()
            ids = ids[-limit:]  # last N emails

            emails = []
            for mid in reversed(ids):
                _, data = mail.fetch(mid, "(RFC822)")
                raw = data[0][1]
                msg = email.message_from_bytes(raw)

                subject = self._decode_header(msg.get("Subject", ""))
                sender = msg.get("From", "")
                body = self._get_body(msg)

                is_qumail = "[QuMail]" in subject or "QuMail Encrypted" in body

                emails.append({
                    "id": mid.decode(),
                    "subject": subject,
                    "from": sender,
                    "body": body,
                    "is_qumail": is_qumail,
                })

            mail.logout()
            return {"success": True, "emails": emails}

        except imaplib.IMAP4.error as e:
            return {"success": False, "message": f"IMAP error: {str(e)}", "emails": []}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}", "emails": []}

    def _decode_header(self, header_val: str) -> str:
        decoded, encoding = decode_header(header_val)[0]
        if isinstance(decoded, bytes):
            return decoded.decode(encoding or 'utf-8', errors='replace')
        return decoded or ""

    def _get_body(self, msg) -> str:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        return part.get_payload(decode=True).decode('utf-8', errors='replace')
                    except Exception:
                        pass
        else:
            try:
                return msg.get_payload(decode=True).decode('utf-8', errors='replace')
            except Exception:
                return msg.get_payload() or ""
        return ""

    def decrypt_email(self, email_body: str, key_hex: str) -> dict:
        """Decrypt a QuMail email using the provided hex key"""
        try:
            from security.encryption_engine import EncryptionEngine, OTPEngine
            payload = SecurePayload.decode(email_body)
            key_bytes = bytes.fromhex(key_hex)

            algo = payload["security_level"]
            encrypted_data = payload["encrypted"]

            if algo in ("QUANTUM_AES", "PQC"):
                engine = EncryptionEngine()
                plaintext = engine.decrypt(encrypted_data, key_bytes)
            elif algo == "QUANTUM_OTP":
                engine = OTPEngine()
                plaintext = engine.decrypt(encrypted_data, key_bytes)
            else:
                plaintext = encrypted_data.get("plaintext", "")

            return {
                "success": True,
                "plaintext": plaintext,
                "key_id": payload.get("key_id"),
                "security_level": algo,
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
