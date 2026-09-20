"""The built front end, as it is actually served.

Everything else in this suite runs with ``VITE_DEV=true``, where the document
points at the Vite dev server and no build is involved. That leaves the
production path — manifest lookup, URL construction, static mount — completely
untested, and it is the path with the most ways to be quietly wrong: a
mismatched entry name, an asset prefix that does not line up with the mount
point, a manifest Vite moved. Each of those renders a page that looks fine and
runs no JavaScript.

These skip when there is no build, so a clean checkout is not blocked by them.
CI builds first, so CI runs them.
"""

from __future__ import annotations

import json
import re

import pytest

from app.inertia import BUILD_DIR, ENTRY, MANIFEST

pytestmark = pytest.mark.skipif(
    not MANIFEST.is_file(),
    reason="no production build — run `npm run build` to exercise these",
)


@pytest.fixture
def built_client(tmp_path, monkeypatch):
    """A client serving the real build rather than the dev server."""
    monkeypatch.setenv("VITE_DEV", "false")
    monkeypatch.setenv("DATABASE_URL", f"sqlite://{tmp_path / 'built.db'}")

    from sillo.testclient import TestClient

    from app.bootstrap import create_app

    with TestClient(create_app()) as client:
        yield client


def asset_urls(html: str) -> list[str]:
    return re.findall(r'<(?:script|link)[^>]*(?:src|href)="(/assets/[^"]+)"', html)


class TestTheManifest:
    def test_it_names_the_entry_the_python_side_looks_up(self):
        """The one string that has to agree in three places.

        vite.config.ts declares the input, app/inertia.py declares ENTRY, and
        the manifest is keyed by it. When they drift, development still works
        — the dev server serves by path — and production renders a page with
        no script tag at all.
        """
        manifest = json.loads(MANIFEST.read_text())

        assert ENTRY in manifest, f"manifest keys: {list(manifest)}"


class TestTheDocument:
    def test_it_references_no_dev_server(self, built_client):
        html = built_client.get("/").text

        assert "5173" not in html
        assert "@vite/client" not in html

    def test_it_references_the_hashed_files(self, built_client):
        urls = asset_urls(built_client.get("/").text)

        assert any(url.endswith(".js") for url in urls)
        assert any(url.endswith(".css") for url in urls), "the stylesheet is missing"

    def test_every_asset_it_references_is_actually_served(self, built_client):
        """The mount point and the asset prefix have to agree.

        `/assets` is served from the `assets` directory *inside* the build
        output, because the adapter strips the leading `assets/` from each
        manifest entry before prefixing. Mount one level up and every one of
        these 404s while the manifest stays perfectly correct.
        """
        html = built_client.get("/").text

        for url in asset_urls(html):
            response = built_client.get(url)
            assert response.status_code == 200, f"{url} is referenced but not served"

    def test_the_javascript_is_served_as_javascript(self, built_client):
        """A wrong content type makes the browser refuse a module script."""
        script = next(url for url in asset_urls(built_client.get("/").text) if url.endswith(".js"))

        content_type = built_client.get(script).headers["content-type"]
        assert "javascript" in content_type


class TestTheBuildOutput:
    def test_the_assets_directory_is_where_the_mount_expects(self):
        assert (BUILD_DIR / "assets").is_dir()
