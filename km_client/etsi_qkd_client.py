"""
ETSI GS QKD 014 Client
Wraps the KM Simulator with ETSI-compliant interface.
In production, this would make REST API calls to actual QKD hardware.
"""

from km_client.km_simulator import get_km_instance


class ETSIQKDClient:
    """
    ETSI GS QKD 014 compliant key retrieval client.
    Interface: get_key(), get_key_with_id(), status()
    """

    def __init__(self):
        self.km = get_km_instance()

    def get_key(self) -> dict:
        """Retrieve a new quantum key (ETSI QKD 014 - GET Key)"""
        result = self.km.get_key()
        return {
            "key_id": result["key_id"],
            "key_bytes": result["key"],
            "key_hex": result["key_hex"],
            "key_size_bits": result["key_size_bits"],
            "source": "ETSI-QKD-014-Simulated",
        }

    def get_key_with_id(self, key_id: str) -> dict:
        """Retrieve a specific key by ID (for synchronized decryption)"""
        result = self.km.get_key(key_id=key_id)
        return {
            "key_id": result["key_id"],
            "key_bytes": result["key"],
            "key_hex": result["key_hex"],
            "key_size_bits": result["key_size_bits"],
            "source": "ETSI-QKD-014-Simulated",
        }

    def status(self) -> dict:
        """Get Key Manager status"""
        return self.km.status()

    def replenish_keys(self, count: int = 20):
        """Request more keys from QKD hardware"""
        self.km.add_keys(count)
        return {"added": count}
