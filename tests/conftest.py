"""Shared fixtures.

The application is built per test through ``create_app`` so no state leaks
between them, and ``TestClient`` is entered as a context manager because that
is what runs the ASGI lifespan — which is what opens the database.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

#: Project packages that read configuration at import time.
PROJECT_PACKAGES = ("app", "routes", "database")


@pytest.fixture(autouse=True)
def _isolated_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Give each test its own database, and pin the settings it depends on.

    These are set before ``app.config`` is imported by the application
    factory, so they win over whatever ``.env`` the developer running the
    suite happens to have.

    ``VITE_DEV`` matters more than it looks. With it false the adapter reads
    the Vite manifest while rendering the first page, so the whole suite would
    depend on ``npm run build`` having been run — and would fail on a clean
    checkout with a FileNotFoundError that says nothing about the test.

    The module purge is what makes the per-test database real. ``app.config``
    builds its ``config`` object once, at import, so without this only the
    first test to import it gets the ``DATABASE_URL`` set here — every test
    after it quietly shares that one database, and rows created by one test
    are visible to the next. It is a slow, confusing failure to diagnose: each
    test passes alone and the suite fails together.
    """
    monkeypatch.setenv("DATABASE_URL", f"sqlite://{tmp_path / 'test.db'}")
    monkeypatch.setenv("DB_GENERATE_SCHEMAS", "true")
    monkeypatch.setenv("VITE_DEV", "true")
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-not-used-anywhere-real")

    _purge_project_modules()
    yield
    # Purged on the way out too, so the next test imports against its own
    # environment rather than inheriting this one's already-imported modules.
    _purge_project_modules()


def _purge_project_modules() -> None:
    for name in list(sys.modules):
        if name.split(".")[0] in PROJECT_PACKAGES:
            del sys.modules[name]


@pytest.fixture
def app():
    """A fresh application instance."""
    from app.bootstrap import create_app

    return create_app()


@pytest.fixture
def client(app):
    """A test client with the application lifespan running."""
    from sillo.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def submit(client):
    """POST the way a browser running Inertia does.

    CSRF here is a double-submit cookie: the middleware sets ``XSRF-TOKEN`` on
    every response and, on an unsafe method, requires the same value back in
    the ``X-XSRF-TOKEN`` header. In the browser axios does that automatically,
    which is the whole reason the cookie is named the way it is. A test client
    runs no JavaScript, so it has to do it by hand — and a test that forgets
    gets a bare 403 that says nothing about why.

    The GET is what mints the cookie. Without a prior safe request there is
    nothing to echo.
    """

    def _submit(url: str, **kwargs):
        if "XSRF-TOKEN" not in client.cookies:
            client.get("/")
        headers = {
            "X-XSRF-TOKEN": client.cookies["XSRF-TOKEN"],
            **kwargs.pop("headers", {}),
        }
        kwargs.setdefault("follow_redirects", False)
        return client.post(url, headers=headers, **kwargs)

    return _submit


@pytest.fixture
def inertia_get(client):
    """Perform a visit the way Inertia's client does.

    The ``X-Inertia`` header is the whole difference between getting an HTML
    document and getting the page object as JSON. A test that omits it is
    testing the first-visit path, whatever it thinks it is testing.
    """

    def visit(url: str, **kwargs):
        headers = {"X-Inertia": "true", "X-Inertia-Version": "dev", **kwargs.pop("headers", {})}
        return client.get(url, headers=headers, **kwargs)

    return visit
