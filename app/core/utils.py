"""
Common utility functions for SkyrisReward backend.
"""
import hashlib
from datetime import datetime
from typing import Any

# Example: hash password (for demo, use passlib in production)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Example: get current UTC time as ISO string
def utcnow_iso() -> str:
    return datetime.utcnow().isoformat()

# Example: pagination helper
def paginate(items: list, skip: int = 0, limit: int = 10) -> list:
    return items[skip:skip+limit]

# Example: safe get from dict
def safe_get(d: dict, key: Any, default=None):
    return d[key] if key in d else default
