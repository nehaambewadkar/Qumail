"""
QuMail Configuration Settings
Edit these to match your email provider settings.
"""

# ─── Gmail SMTP/IMAP Settings ─────────────────────────────────────────────────
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465           # SSL
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993           # SSL

# ─── Key Manager Settings ─────────────────────────────────────────────────────
KM_BASE_URL = "http://127.0.0.1:5000/api/v1"
DEFAULT_AES_KEY_SIZE = 32    # bytes (256-bit)
DEFAULT_SECURITY_LEVEL = "QUANTUM_AES"

# ─── Flask Settings ───────────────────────────────────────────────────────────
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = False
