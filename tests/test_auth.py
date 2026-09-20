"""Sign up, sign in, sign out — and the redirect-with-errors dance.

The thing worth testing here is not that authentication works. It is that a
*failed* submission behaves the way Inertia requires: a 303 back to the form,
with the errors waiting in the session for the page that follows, and cleared
once that page has read them.

Every POST goes through the ``submit`` fixture, which attaches the CSRF header
the way axios does in the browser. ``client.post`` directly is a 403.
"""

from __future__ import annotations

import pytest

GOOD = {
    "email": "ada@example.com",
    "username": "ada",
    "password": "correct-horse",
    "full_name": "Ada Lovelace",
}

LOGIN = {"email": GOOD["email"], "password": GOOD["password"]}


@pytest.fixture
def registered(submit):
    """An account that already exists, created through the real endpoint."""
    response = submit("/register", json=GOOD)
    assert response.status_code == 303, response.text
    # Sign back out, so a test starts as a guest unless it says otherwise.
    submit("/logout")
    return GOOD


def props(client, url="/dashboard"):
    """The props of a page, fetched the way Inertia's client fetches it."""
    response = client.get(
        url,
        headers={"X-Inertia": "true", "X-Inertia-Version": "dev"},
        follow_redirects=False,
    )
    return response.json()["props"]


class TestRegistration:
    def test_a_valid_sign_up_redirects_to_the_dashboard(self, submit):
        response = submit("/register", json=GOOD)

        assert response.status_code == 303
        assert response.headers["location"] == "/dashboard"

    def test_the_redirect_is_303_not_302(self, submit):
        """Not decoration.

        On a 302 the browser repeats the POST against the new URL, so a
        successful sign-up would be attempted a second time.
        """
        assert submit("/register", json=GOOD).status_code == 303

    def test_the_new_user_is_signed_in(self, client, submit):
        submit("/register", json=GOOD)

        user = props(client)["auth"]["user"]
        assert user["email"] == GOOD["email"]
        assert user["username"] == GOOD["username"]

    def test_the_password_never_reaches_the_client(self, client, submit):
        """`current_user` lists its fields by hand precisely so this holds."""
        submit("/register", json=GOOD)

        user = props(client)["auth"]["user"]
        assert not any("password" in key for key in user)

    @pytest.mark.parametrize(
        ("payload", "field"),
        [
            ({**GOOD, "email": ""}, "email"),
            ({**GOOD, "email": "not-an-address"}, "email"),
            ({**GOOD, "username": ""}, "username"),
            ({**GOOD, "username": "ab"}, "username"),
            ({**GOOD, "password": ""}, "password"),
            ({**GOOD, "password": "short"}, "password"),
        ],
    )
    def test_invalid_input_goes_back_with_an_error_on_that_field(
        self, client, submit, payload, field
    ):
        response = submit("/register", json=payload)

        assert response.status_code == 303
        assert field in props(client, "/register")["errors"]

    def test_every_problem_is_reported_at_once(self, client, submit):
        """A form that reveals one fault at a time takes as many submissions."""
        submit("/register", json={"email": "", "username": "", "password": ""})

        errors = props(client, "/register")["errors"]
        assert set(errors) == {"email", "username", "password"}

    def test_a_duplicate_email_is_refused(self, client, submit, registered):
        submit("/register", json={**GOOD, "username": "other"})

        assert "email" in props(client, "/register")["errors"]

    def test_a_duplicate_username_is_refused(self, client, submit, registered):
        submit("/register", json={**GOOD, "email": "someone@example.com"})

        assert "username" in props(client, "/register")["errors"]


class TestSignIn:
    def test_correct_credentials_start_a_session(self, client, submit, registered):
        response = submit("/login", json=LOGIN)

        assert response.status_code == 303
        assert response.headers["location"] == "/dashboard"
        assert props(client)["auth"]["user"]["email"] == GOOD["email"]

    def test_the_email_is_matched_case_insensitively(self, submit, registered):
        response = submit("/login", json={**LOGIN, "email": "ADA@EXAMPLE.COM"})

        assert response.headers["location"] == "/dashboard"

    def test_a_wrong_password_is_refused(self, client, submit, registered):
        submit("/login", json={**LOGIN, "password": "wrong"})

        assert props(client, "/login")["auth"]["user"] is None

    def test_an_unknown_account_and_a_wrong_password_say_the_same_thing(
        self, client, submit, registered
    ):
        """Otherwise the sign-in form answers "does this address have an
        account here?" for anyone who cares to ask."""
        submit("/login", json={**LOGIN, "password": "wrong"})
        wrong_password = props(client, "/login")["errors"]

        submit("/login", json={"email": "nobody@example.com", "password": "wrong"})
        no_such_user = props(client, "/login")["errors"]

        assert wrong_password == no_such_user
        assert wrong_password != {}

    def test_a_form_post_works_as_well_as_json(self, submit, registered):
        """The no-JavaScript path, and what `curl -d` sends."""
        response = submit("/login", data=LOGIN)

        assert response.headers["location"] == "/dashboard"


class TestSignOut:
    def test_it_ends_the_session(self, client, submit, registered):
        submit("/login", json=LOGIN)
        assert props(client)["auth"]["user"] is not None

        submit("/logout")

        assert props(client, "/")["auth"]["user"] is None

    def test_signing_out_while_signed_out_is_harmless(self, submit):
        """`session_logout` raises KeyError on a missing key, so the guard in
        the handler is what keeps this a redirect rather than a 500."""
        assert submit("/logout").status_code == 303


class TestGuards:
    def test_the_dashboard_sends_a_guest_to_the_login_page(self, client):
        """A redirect, not a 401.

        Sillo's `auth=` route argument answers 401, which Inertia's client
        surfaces as an error modal rather than a login screen. For a page, the
        guard has to redirect.
        """
        response = client.get("/dashboard", follow_redirects=False)

        assert response.status_code == 302
        assert response.headers["location"] == "/login"

    def test_a_signed_in_user_is_kept_off_the_login_page(self, client, submit, registered):
        submit("/login", json=LOGIN)

        response = client.get("/login", follow_redirects=False)

        assert response.status_code == 302
        assert response.headers["location"] == "/dashboard"


class TestCsrf:
    """The protection the ``submit`` fixture exists to satisfy."""

    def test_a_post_without_the_header_is_rejected(self, client):
        client.get("/")  # mints the cookie

        response = client.post("/login", json=LOGIN, follow_redirects=False)

        assert response.status_code == 403

    def test_a_post_with_a_forged_header_is_rejected(self, client):
        client.get("/")

        response = client.post(
            "/login",
            json=LOGIN,
            headers={"X-XSRF-TOKEN": "not-the-token"},
            follow_redirects=False,
        )

        assert response.status_code == 403

    def test_the_cookie_is_readable_by_javascript(self, client):
        """axios cannot attach a header from a cookie the browser hides.

        This is the one cookie that is deliberately not httponly, and it is
        safe because the token is useless without the session cookie — which
        stays httponly.
        """
        header = client.get("/").headers.get_list("set-cookie")
        xsrf = next(value for value in header if value.startswith("XSRF-TOKEN="))

        assert "httponly" not in xsrf.lower()

    def test_the_session_cookie_is_not_readable_by_javascript(self, client, submit, registered):
        submit("/login", json=LOGIN)
        response = client.get("/", follow_redirects=False)

        session = [
            value
            for value in response.headers.get_list("set-cookie")
            if value.startswith("session_id=")
        ]
        assert all("httponly" in value.lower() for value in session)

    def test_a_get_needs_no_token(self, client):
        """Safe methods are exempt, or every first visit would fail."""
        assert client.get("/").status_code == 200


class TestFlash:
    """Values that survive exactly one redirect."""

    def test_errors_are_cleared_once_read(self, client, submit):
        """Otherwise a validation error reappears on the next page visited."""
        submit("/register", json={**GOOD, "email": ""})

        assert "email" in props(client, "/register")["errors"]
        assert props(client, "/register")["errors"] == {}

    def test_a_success_message_survives_the_redirect(self, client, submit):
        submit("/register", json=GOOD)

        assert props(client)["flash"]["success"]

    def test_and_is_gone_on_the_next_page(self, client, submit):
        submit("/register", json=GOOD)
        props(client)

        assert props(client)["flash"]["success"] is None
