"""
Quantum Key Manager Simulator
Simulates an ETSI GS QKD 014 compliant Key Management System.
In production, this connects to actual QKD hardware.
"""

import os
import uuid
import time
import threading


class KMSimulator:
    """
    In-memory quantum key store that simulates a QKD Key Manager.
    Generates cryptographically secure random keys (simulating quantum randomness).
    """

    def __init__(self, key_size_bytes: int = 32, pool_size: int = 100):
        self.key_size = key_size_bytes
        self.key_pool = {}       # key_id -> key_bytes
        self.used_keys = set()   # consumed key IDs
        self.lock = threading.Lock()
        self._fill_pool(pool_size)

    def _generate_quantum_key(self) -> tuple:
        """Generate a 'quantum' key (CSRNG in simulation)"""
        key_id = str(uuid.uuid4())
        key_bytes = os.urandom(self.key_size)
        return key_id, key_bytes

    def _fill_pool(self, count: int):
        """Pre-fill the key pool"""
        for _ in range(count):
            key_id, key_bytes = self._generate_quantum_key()
            self.key_pool[key_id] = key_bytes

    def get_key(self, key_id: str = None) -> dict:
        """
        Retrieve a key by ID (ETSI QKD 014 GET_KEY).
        If key_id is None, returns a fresh key.
        """
        with self.lock:
            if key_id:
                if key_id in self.used_keys:
                    raise ValueError(f"Key {key_id} already consumed (one-time use)")
                if key_id not in self.key_pool:
                    raise ValueError(f"Key {key_id} not found")
                key_bytes = self.key_pool.pop(key_id)
                self.used_keys.add(key_id)
            else:
                if not self.key_pool:
                    self._fill_pool(10)
                key_id, key_bytes = next(iter(self.key_pool.items()))
                del self.key_pool[key_id]
                self.used_keys.add(key_id)

            return {
                "key_id": key_id,
                "key": key_bytes,
                "key_hex": key_bytes.hex(),
                "key_size_bits": len(key_bytes) * 8,
                "timestamp": time.time(),
            }

    def status(self) -> dict:
        """Return KM status"""
        with self.lock:
            return {
                "available_keys": len(self.key_pool),
                "consumed_keys": len(self.used_keys),
                "key_size_bits": self.key_size * 8,
                "status": "operational",
            }

    def add_keys(self, count: int = 10):
        """Generate more keys"""
        with self.lock:
            for _ in range(count):
                key_id, key_bytes = self._generate_quantum_key()
                self.key_pool[key_id] = key_bytes


# Global singleton instance
_km_instance = None

def get_km_instance() -> KMSimulator:
    global _km_instance
    if _km_instance is None:
        _km_instance = KMSimulator()
    return _km_instance
