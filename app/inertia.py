"""The Inertia adapter, configured once.

This module owns the single :class:`Inertia` instance and the props every page
receives. Route modules do not import it — they call the module-level
``render`` from ``sillo_inertia``, which finds this adapter through the
middleware handling the request. That keeps ``routes/`` free of any import back
into ``app/``, and so free of the circular import it would otherwise cause.
"""

from __future__ import annotations

from typing import Any

from sillo.core.http import Request
from sillo_inertia import Inertia, vite_react

from app.config import BASE_DIR, config

#: Where the compiled front end is written, and where its manifest lands.
#:
#: Vite writes the manifest to ``.vite/manifest.json`` *inside* the output
#: directory as of Vite 5 — it used to sit at the root of it. The adapter is
#: given the full path rather than a directory so a Vite upgrade that moves it
#: again fails loudly here instead of rendering a page with no script tag.
BUILD_DIR = BASE_DIR / "static" / "build"
MANIFEST = BUILD_DIR / ".vite" / "manifest.json"

#: The client entry, as a path relative to the project root.
#:
#: This exact string is the key Vite writes into the manifest, and the path the
#: dev server serves from. It has to match ``build.rollupOptions.input`` in
#: vite.config.ts; if the two drift, development still works and production
#: renders a page with no JavaScript.
ENTRY = "js/main.tsx"


def build_inertia() -> Inertia:
    """Construct the adapter for this project."""
    return Inertia(
        # Attached in bootstrap rather than here. Passing `app=` would install
        # the middleware at construction time, which puts it at the wrong place
        # in a chain that is ordered deliberately.
        root_view=BASE_DIR / "root.html",
        # An absolute base_dir. Left unset the adapter derives one by walking
        # three parents up from the root view, which is correct only when the
        # process was started from the project root.
        base_dir=BASE_DIR,
        version=config.asset_version,
        root_id="app",
        # Substituted into root.html as `{{ app_name }}`.
        # View data and props are different channels: props reach React, view
        # data only ever reaches the HTML shell. The document title belongs in
        # the shell, so that a page has a title before any JavaScript runs.
        view_data={"app_name": config.app_name},
        vite=vite_react(
            entry=ENTRY,
            dev_server=config.vite_dev_server,
            manifest_path=MANIFEST,
            asset_prefix="/assets/",
            dev=config.vite_dev,
        ),
    )


def share_globals(inertia: Inertia) -> None:
    """Register the props every page receives.

    These are resolved per request even though they are registered once: a
    callable prop is called each time a page is rendered, so ``auth`` reflects
    whoever is making *this* request rather than whoever was making the one
    during startup.
    """
    inertia.share(
        app_name=config.app_name,
        auth=lambda request: {"user": current_user(request)},
        # Every page reads `errors`, so it must always be present — a React
        # component that does `errors.email` cannot be written defensively at
        # every use site. Consumed here, which is what makes it flash: the
        # values survive exactly one render and are cleared as they are read.
        errors=lambda request: take_flash(request, "errors") or {},
        flash=lambda request: {
            "success": take_flash(request, "success"),
            "error": take_flash(request, "error"),
        },
    )


def current_user(request: Request) -> dict[str, Any] | None:
    """The authenticated user as plain JSON, or None.

    Returns a dict rather than the model. Props are serialised to JSON and
    handed to the browser, so anything on the model that is not meant to be
    public — the password hash above all — must not be in what this returns.
    Listing the fields explicitly is what guarantees that; a `to_dict()` would
    quietly start shipping every column you add later.
    """
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return None
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": getattr(user, "full_name", None),
        "is_staff": bool(getattr(user, "is_staff", False)),
    }


# -- flash -----------------------------------------------------------------
#
# Inertia has no way to return a validation error from a POST directly: a
# failed submission redirects back, and the errors have to survive that one
# redirect. The session is where they wait.


def flash(request: Request, key: str, value: Any) -> None:
    """Store a value for the next request only."""
    request.session[_flash_key(key)] = value


def take_flash(request: Request, key: str) -> Any:
    """Read a flashed value and remove it.

    Reading is destructive on purpose — a validation error that stayed in the
    session would reappear on the next page the user visited.

    ``Session`` has ``get`` and ``delete`` but no ``pop``, so this is the two
    calls that would otherwise be written at every use site.
    """
    session = getattr(request, "session", None)
    if session is None:
        return None
    stored = session.get(_flash_key(key))
    if stored is not None:
        session.delete(_flash_key(key))
    return stored


def _flash_key(key: str) -> str:
    return f"_flash_{key}"
