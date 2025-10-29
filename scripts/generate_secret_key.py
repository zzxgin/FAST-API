"""Script to generate a secure SECRET_KEY for FastAPI/JWT usage.

Usage:
    python scripts/generate_secret_key.py
"""

import secrets

def generate_secret_key(length: int = 32) -> str:
    """Generate a secure random URL-safe secret key.

    Args:
        length: Number of bytes for the key (default 32).
    Returns:
        str: URL-safe base64 encoded secret key.
    """
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    print(generate_secret_key())
