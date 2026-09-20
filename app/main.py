"""ASGI entrypoint.

This module exposes ``app`` for the server to import:

    uvicorn app.main:app --reload

Run ``npm run dev`` alongside it. The page loads its JavaScript from the Vite
dev server, so without it every route renders an empty document.

Assembly lives in ``app.bootstrap`` so that importing this module has no side
effects beyond building the application.
"""

from __future__ import annotations

from app.bootstrap import create_app
from app.config import config

app = create_app()


if __name__ == "__main__":
    app.run(host=config.host, port=config.port, reload=config.debug)
