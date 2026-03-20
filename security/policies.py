"""Security level definitions for QuMail"""

from enum import Enum

class SecurityLevel(Enum):
    QUANTUM_AES = "QUANTUM_AES"   # AES-256-GCM + QKD keys (Recommended)
    QUANTUM_OTP = "QUANTUM_OTP"   # One-Time Pad with quantum keys
    PQC = "PQC"                   # Post-Quantum Cryptography (simulated)
    NO_SECURITY = "NO_SECURITY"   # Plain text (testing only)

SECURITY_DESCRIPTIONS = {
    SecurityLevel.QUANTUM_AES: "AES-256-GCM with Quantum Key Distribution",
    SecurityLevel.QUANTUM_OTP: "One-Time Pad with Quantum Keys (Perfect Secrecy)",
    SecurityLevel.PQC: "Post-Quantum Cryptography (Kyber + AES hybrid)",
    SecurityLevel.NO_SECURITY: "No Encryption (Testing Only)",
}
