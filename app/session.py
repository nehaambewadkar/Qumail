"""User session management for QuMail"""

from dataclasses import dataclass, field
from typing import Optional, List
import time


@dataclass
class EmailSession:
    """Holds user credentials and sent email log for a session"""
    email: str = ""
    app_password: str = ""
    authenticated: bool = False
    sent_log: List[dict] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def log_sent(self, to: str, subject: str, key_id: str, key_hex: str, security_level: str):
        self.sent_log.append({
            "timestamp": time.time(),
            "to": to,
            "subject": subject,
            "key_id": key_id,
            "key_hex": key_hex,
            "security_level": security_level,
        })

    def get_last_sent(self) -> Optional[dict]:
        return self.sent_log[-1] if self.sent_log else None


# In-memory session store (keyed by session_id)
_sessions: dict = {}


def create_session(session_id: str, email: str, app_password: str) -> EmailSession:
    session = EmailSession(email=email, app_password=app_password, authenticated=True)
    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> Optional[EmailSession]:
    return _sessions.get(session_id)


def clear_session(session_id: str):
    _sessions.pop(session_id, None)
