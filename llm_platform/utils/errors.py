"""Platform-specific exceptions."""

from __future__ import annotations


class PlatformError(Exception):
    """Base platform exception."""


class NotFoundError(PlatformError):
    """Raised when a resource does not exist."""


class ConflictError(PlatformError):
    """Raised when a duplicate or conflicting state is detected."""


class ValidationError(PlatformError):
    """Raised when validation fails outside Pydantic models."""


class RoutingError(PlatformError):
    """Raised when routing cannot find an eligible deployment."""
