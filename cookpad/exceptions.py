from __future__ import annotations


class CookpadError(Exception):
    """Base exception for cookpad-py."""


class AuthenticationError(CookpadError):
    """Authentication failed (401)."""


class NotFoundError(CookpadError):
    """Resource not found (404)."""


class RateLimitError(CookpadError):
    """Rate limit exceeded (429)."""


class APIError(CookpadError):
    """General API error."""

    def __init__(self, message: str, status_code: int = 0) -> None:
        self.status_code = status_code
        super().__init__(message)
