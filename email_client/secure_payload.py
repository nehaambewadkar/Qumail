"""
Secure Payload - wraps encrypted data for email transmission.
The encrypted email body is a JSON payload wrapped in plain-text markers.
"""

import json
import base64
from config.constants import QUMAIL_HEADER, QUMAIL_FOOTER, PAYLOAD_VERSION


class SecurePayload:
    """Serialize and deserialize QuMail encrypted email payloads"""

    @staticmethod
    def encode(
        encrypted_data: dict,
        key_id: str,
        security_level: str,
        original_subject: str = "",
    ) -> str:
        """
        Encode encrypted data as an email-safe text payload.
        Returns a string that can be placed in the email body.
        """
        payload = {
            "version": PAYLOAD_VERSION,
            "security_level": security_level,
            "key_id": key_id,
            "subject": original_subject,
            "encrypted": encrypted_data,
        }
        payload_json = json.dumps(payload, indent=2)
        payload_b64 = base64.b64encode(payload_json.encode()).decode()

        return f"""{QUMAIL_HEADER}
Version: {PAYLOAD_VERSION}
Security: {security_level}
Key-ID: {key_id}

{payload_b64}

{QUMAIL_FOOTER}

This email was encrypted with QuMail (Quantum Secure Email Client).
To decrypt, use the QuMail decryption tool with your encryption key.
"""

    @staticmethod
    def decode(email_body: str) -> dict:
        """
        Parse a QuMail encrypted email body.
        Returns the payload dict or raises ValueError if not a QuMail email.
        """
        if QUMAIL_HEADER not in email_body:
            raise ValueError("Not a QuMail encrypted email")

        lines = email_body.split('\n')
        b64_lines = []
        in_payload = False

        for line in lines:
            stripped = line.strip()
            if stripped == QUMAIL_HEADER:
                in_payload = True
                continue
            if stripped == QUMAIL_FOOTER:
                break
            if in_payload and stripped and not stripped.startswith(('Version:', 'Security:', 'Key-ID:')):
                b64_lines.append(stripped)

        if not b64_lines:
            raise ValueError("Could not find payload in email body")

        payload_b64 = ''.join(b64_lines)
        payload_json = base64.b64decode(payload_b64).decode()
        return json.loads(payload_json)
