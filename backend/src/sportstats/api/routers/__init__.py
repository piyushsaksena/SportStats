"""Routers package."""

from sportstats.api.routers import (
    admin,
    ai,
    analytics,
    editions,
    participants,
    sources,
    sports,
    tournaments,
)

__all__ = [
    "sports",
    "tournaments",
    "editions",
    "participants",
    "analytics",
    "sources",
    "admin",
    "ai",
]
