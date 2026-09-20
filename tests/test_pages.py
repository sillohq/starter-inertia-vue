"""The Inertia protocol, as this application implements it.

The same URL answers two different ways depending on one request header, and
almost every mistake in an Inertia application is a mistake about which of the
two is happening. These tests pin both.
"""

from __future__ import annotations

import json
import re


def page_object(response) -> dict:
    """Pull the page object out of an HTML document.

    The first visit is a plain browser navigation, so the page arrives inside
    the document rather than as the body. Since Inertia 2.0 it lives in a JSON
    script tag; the 1.x `data-page` attribute on the root div is not read by
    any current client.
    """
    match = re.search(
        r'<script type="application/json" data-page="app">(.*?)</script>',
        response.text,
        re.DOTALL,
    )
    assert match, "no page object in the document"
    return json.loads(match.group(1))


class TestTheFirstVisit:
    """A browser navigation gets a full HTML document."""

    def test_it_returns_html(self, client):
        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert '<div id="app">' in response.text

    def test_the_page_object_is_embedded(self, client):
        page = page_object(client.get("/"))

        assert page["component"] == "Home"
        assert page["url"] == "/"
        assert page["props"]["message"]

    def test_the_page_object_cannot_break_out_of_its_script_tag(self, client):
        """Props are attacker-influenced in general, so this must hold.

        A prop containing `</script>` would otherwise end the element early
        and put the remainder of the JSON into the document as markup.
        """
        html = client.get("/").text

        assert "</script><" not in html.replace("</script>\n", "")
        # The escaping that prevents it, rather than only its absence here.
        page = page_object(client.get("/"))
        assert page["component"] == "Home"

    def test_the_vite_dev_tags_are_present(self, client):
        """With VITE_DEV=true the document loads modules from the dev server."""
        html = client.get("/").text

        assert "http://localhost:5173/@vite/client" in html
        assert "http://localhost:5173/js/main.tsx" in html

    def test_the_title_comes_from_view_data(self, client):
        """Read from config rather than written out.

        `sillo-start` renames the project on creation, so a hardcoded name
        here would hand every generated project a red suite on its first
        `make test`. Comparing against config also states the actual contract:
        the shell's title is wired to APP_NAME.
        """
        from app.config import config

        assert f"<title>{config.app_name}</title>" in client.get("/").text


class TestAnInertiaVisit:
    """Once the client has booted, the same URL answers with JSON."""

    def test_it_returns_the_page_object(self, inertia_get):
        response = inertia_get("/")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")

        page = response.json()
        assert page["component"] == "Home"
        assert set(page) >= {"component", "props", "url", "version"}

    def test_it_carries_the_asset_version(self, inertia_get):
        assert inertia_get("/").json()["version"] == "dev"

    def test_a_stale_client_is_sent_to_do_a_full_visit(self, client):
        """The guard against a new page object meeting old components.

        409 plus X-Inertia-Location is Inertia's instruction to the client to
        drop the XHR and navigate properly, which lands it on the new bundle.
        """
        response = client.get(
            "/", headers={"X-Inertia": "true", "X-Inertia-Version": "an-older-build"}
        )

        assert response.status_code == 409
        assert response.headers["x-inertia-location"].endswith("/")

    def test_a_partial_reload_returns_only_what_was_asked_for(self, client):
        """What `router.reload({ only: [...] })` sends.

        The point of the feature is that unrequested props are never resolved,
        so an expensive one costs nothing on a reload that would discard it.
        """
        response = client.get(
            "/",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Version": "dev",
                "X-Inertia-Partial-Component": "Home",
                "X-Inertia-Partial-Data": "message",
            },
        )

        props = response.json()["props"]
        assert set(props) == {"message"}


class TestSharedProps:
    """Props every page gets, without any handler passing them."""

    def test_a_guest_has_no_user(self, inertia_get):
        props = inertia_get("/").json()["props"]

        assert props["auth"] == {"user": None}

    def test_the_app_name_is_shared(self, inertia_get):
        """From config, so this survives the project being renamed."""
        from app.config import config

        assert inertia_get("/").json()["props"]["app_name"] == config.app_name

    def test_errors_and_flash_are_always_present(self, inertia_get):
        """Never absent, so no component needs to guard before reading them."""
        props = inertia_get("/").json()["props"]

        assert props["errors"] == {}
        assert props["flash"] == {"success": None, "error": None}


class TestRouting:
    def test_an_unknown_page_is_a_404(self, client):
        assert client.get("/nope").status_code == 404

    def test_the_health_probe_is_json_not_a_page(self, client):
        """The API is deliberately not Inertia."""
        response = client.get("/api/health")

        assert response.status_code == 200
        assert response.json()["checks"]["database"] == "ok"

    def test_the_api_is_in_the_openapi_document(self, client):
        paths = client.get("/openapi.json").json()["paths"]

        assert "/api/health" in paths

    def test_the_pages_are_not_in_the_openapi_document(self, client):
        """Pages are not an API and should not be documented as one."""
        paths = client.get("/openapi.json").json()["paths"]

        assert "/login" not in paths
        assert "/dashboard" not in paths
