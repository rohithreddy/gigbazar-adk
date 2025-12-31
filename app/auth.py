import os
from typing import Optional

# Simple in-memory session store for this single-user app
_active_session: Optional[str] = None

USERNAME = os.environ.get("APP_USERNAME", "admin")
PASSWORD = os.environ.get("APP_PASSWORD", "password")

def login(username: str, password: str) -> bool:
    """Simple login function."""
    global _active_session
    if username == USERNAME and password == PASSWORD:
        _active_session = "active"
        return True
    return False

def logout() -> None:
    """Logout function."""
    global _active_session
    _active_session = None

def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return _active_session is not None
