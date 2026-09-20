"""Application configuration.

Settings are declared once here as a typed :class:`sillo.config.Config` and
loaded from ``.env`` at import. Read values from the ``config`` object rather
than calling ``os.getenv`` around the codebase — a typo in an environment
variable name then fails at startup with a clear message instead of silently
becoming ``None`` at request time.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from sillo.config import Config

#: The project root. Every path in this project is resolved from here rather
#: than from the working directory, so `pytest` from a subdirectory and
#: `uvicorn` from the root find the same files.
BASE_DIR = Path(__file__).resolve().parent.parent


class AppConfig(Config):
    """Typed settings for Starter."""

    # -- application ---------------------------------------------------
    app_name: str = "Starter"
    app_env: Literal["local", "testing", "staging", "production"] = "local"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000
    secret_key: str = "change-me"

    # -- database ------------------------------------------------------
    database_url: str = "sqlite://storage/starter.db"
    db_pool_size: int = 5
    db_echo: bool = False
    # Off, because migrations own the schema. Generating it on startup would
    # create tables outside the migration history and have every process race
    # to run DDL. Set DB_GENERATE_SCHEMAS=true for a throwaway database.
    db_generate_schemas: bool = False

    # -- session -------------------------------------------------------
    session_cookie_name: str = "session_id"
    session_lifetime: int = 86400

    # -- inertia / vite ------------------------------------------------
    #: Where the Vite dev server is listening. Only consulted when
    #: ``vite_dev`` is true.
    vite_dev_server: str = "http://localhost:5173"

    #: True  — the page loads its JavaScript from the Vite dev server, with
    #:         hot module replacement. Run `npm run dev` alongside the app.
    #: False — the page loads the hashed files named in the build manifest.
    #:         Requires `npm run build` to have run; without it the first
    #:         page render raises FileNotFoundError on the manifest.
    #:
    #: This is its own flag rather than being derived from ``app_env``
    #: because the two genuinely vary apart: a test run wants `local`
    #: settings with no dev server, and a staging box wants a production
    #: build while still being debuggable.
    vite_dev: bool = True

    #: Sent to the client as the asset version. When it changes, an Inertia
    #: visit gets a 409 and the client does a full reload, which is what
    #: stops a stale bundle from talking to a new API. In production set it
    #: to something that changes per build — a commit SHA works.
    asset_version: str = "dev"

    # -- security ------------------------------------------------------
    cors_allow_origins: str = "http://localhost:5173"

    # -- logging -------------------------------------------------------
    log_level: Literal["debug", "info", "warning", "error"] = "info"


#: Loaded once at import and shared across the application.
#:
#: The env file is passed to the constructor rather than declared on an inner
#: ``class Config``: both work, but the inner-class form is the one Pydantic
#: v2 has deprecated and it would warn on every import.
config = AppConfig(_env_file=".env")


def cors_origins() -> list[str]:
    """Split the comma-separated origin list into the form the middleware wants."""
    return [origin.strip() for origin in config.cors_allow_origins.split(",") if origin.strip()]
