"""Compatibility shim for modules that import `app.db.session`.

This module re-exports the engine and SessionLocal created in
`app.db.database` so existing imports continue to work while the database
package centralizes engine/session creation.
"""

from app.db.database import engine, SessionLocal

__all__ = ["engine", "SessionLocal"]
