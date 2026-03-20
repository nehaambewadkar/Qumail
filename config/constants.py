"""Application constants for QuMail"""

APP_NAME = "QuMail"
APP_VERSION = "1.0"
APP_DESCRIPTION = "Quantum Secure Email Client"

# Encryption
DEFAULT_KEY_SIZE_BYTES = 32   # 256-bit
DEFAULT_KEY_SIZE_BITS = 256
NONCE_SIZE_BYTES = 12
TAG_SIZE_BYTES = 16

# Email payload markers
QUMAIL_HEADER = "--- QuMail Encrypted Message ---"
QUMAIL_FOOTER = "--- End QuMail Message ---"
PAYLOAD_VERSION = "1"

# Key Manager
KM_POOL_SIZE = 100
KM_REPLENISH_THRESHOLD = 10
