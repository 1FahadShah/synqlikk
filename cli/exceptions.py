# cli/exceptions.py

class APIError(Exception):
    """Raised when a server/API call fails."""
    pass

class AuthenticationError(Exception):
    """Raised for login/register failures or invalid session."""
    pass

class SyncConflictError(Exception):
    """Raised when a sync conflict occurs (e.g., last-write-wins needed)."""
    pass
