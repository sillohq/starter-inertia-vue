"""JSON routes.

Kept separate from the Inertia pages, and deliberately small. An Inertia
application does not need an API for its own front end — the page's props
*are* the payload, delivered with the page rather than fetched after it. What
belongs here is what something other than this front end calls: a health probe,
a webhook receiver, a mobile client.

These appear in the OpenAPI document at ``/docs``. The Inertia pages do not,
which is correct — they are not an API.
"""

from __future__ import annotations

from sillo import Router
from sillo.core.http import Request, Response

from app.config import config

router = Router(prefix="/api", tags=["api"])


@router.get("/health", summary="Liveness and readiness probe")
async def health(request: Request, response: Response) -> Response:
    """Report whether the application and its dependencies are reachable."""
    checks: dict[str, str] = {"app": "ok"}

    # Inside a router, `request.app` is the router. `request.base_app` is the
    # application that owns the state `setup_record` wrote to.
    manager = request.base_app.state.get("record")
    checks["database"] = "ok" if manager and await manager.health() else "unavailable"

    healthy = all(status == "ok" for status in checks.values())
    return response.json(
        {"status": "ok" if healthy else "degraded", "checks": checks, "env": config.app_env},
        status_code=200 if healthy else 503,
    )
