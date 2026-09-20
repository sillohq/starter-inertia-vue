"""Sign in, sign up, sign out — the Inertia way.

There is no JSON contract here to speak of. Inertia's client submits a form
and expects one of two things back: a redirect on success, or a redirect
*back* on failure with the errors waiting for the page it returns to. Nothing
renders an error response directly, which is why every failure path below ends
in :func:`back_with_errors` rather than a 422.

The pattern is worth reading once, because it is the part of Inertia that has
no equivalent in a JSON API.
"""

from __future__ import annotations

import re
from typing import Any

from sillo.auth.session_auth import login as session_login
from sillo.auth.session_auth import logout as session_logout
from sillo.core.http import Request, Response
from sillo_inertia import redirect, render

from app.inertia import flash
from database.models.user import User

#: Deliberately permissive. Full RFC 5322 in a regex is a famous mistake, and
#: the only real proof an address works is that mail sent to it arrives.
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

MIN_PASSWORD_LENGTH = 8


# -- pages -----------------------------------------------------------------


async def show_login(request: Request, response: Response):
    """The sign-in form.

    Already signed in? Go to the dashboard. Without this, a signed-in user who
    navigates back to /login sees a form that would sign them in as somebody
    else.
    """
    if request.user.is_authenticated:
        return redirect("/dashboard")
    return await render("auth/Login")


async def show_register(request: Request, response: Response):
    """The sign-up form."""
    if request.user.is_authenticated:
        return redirect("/dashboard")
    return await render("auth/Register")


# -- actions ---------------------------------------------------------------


async def login(request: Request, response: Response):
    """Verify credentials and start a session."""
    data = await _payload(request)
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    errors: dict[str, str] = {}
    if not email:
        errors["email"] = "Enter your email address."
    if not password:
        errors["password"] = "Enter your password."
    if errors:
        return back_with_errors(request, errors, "/login")

    user = await User.objects.get_by_email(email)

    # One message for "no such user" and for "wrong password", on purpose.
    # Distinguishing them turns the sign-in form into a way to ask whether an
    # address has an account here, which is not a question a stranger should
    # be able to ask.
    if user is None or not user.check_password(password):
        return back_with_errors(request, {"email": "Those credentials do not match."}, "/login")

    if not user.is_active:
        return back_with_errors(request, {"email": "This account is disabled."}, "/login")

    session_login(request, user)
    flash(request, "success", f"Welcome back, {user.display_name}.")
    return redirect("/dashboard")


async def register(request: Request, response: Response):
    """Create an account and sign the new user in."""
    data = await _payload(request)
    email = str(data.get("email", "")).strip().lower()
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    full_name = str(data.get("full_name", "")).strip() or None

    errors = await _registration_errors(email, username, password)
    if errors:
        return back_with_errors(request, errors, "/register")

    user = await User.objects.create_user(
        email=email,
        username=username,
        password=password,
        full_name=full_name,
    )

    session_login(request, user)
    flash(request, "success", "Your account is ready.")
    return redirect("/dashboard")


async def logout(request: Request, response: Response):
    """End the session.

    A POST, not a GET. A link that signs you out can be triggered by any page
    that embeds it — including one on another origin, and including a
    prefetcher that follows links on your behalf.
    """
    if request.user.is_authenticated:
        session_logout(request)
    return redirect("/")


# -- helpers ---------------------------------------------------------------


async def _registration_errors(email: str, username: str, password: str) -> dict[str, str]:
    """Every problem with a sign-up, in one pass.

    Returning all of them together rather than the first is not politeness: a
    form that reveals one fault at a time takes as many submissions as it has
    faults.
    """
    errors: dict[str, str] = {}

    if not email:
        errors["email"] = "Enter your email address."
    elif not EMAIL_RE.match(email):
        errors["email"] = "That does not look like an email address."
    elif await User.objects.get_by_email(email):
        errors["email"] = "That email address is already registered."

    if not username:
        errors["username"] = "Choose a username."
    elif len(username) < 3:
        errors["username"] = "Usernames are at least 3 characters."
    elif await User.filter(username=username).exists():
        errors["username"] = "That username is taken."

    if not password:
        errors["password"] = "Choose a password."
    elif len(password) < MIN_PASSWORD_LENGTH:
        errors["password"] = f"Passwords are at least {MIN_PASSWORD_LENGTH} characters."

    return errors


def back_with_errors(request: Request, errors: dict[str, str], fallback: str):
    """Flash validation errors and send the client back to the form.

    Two details make this work, and both are easy to get wrong.

    The status is a **303**, which :func:`redirect` picks automatically after a
    POST. On a 302 the browser repeats the POST against the new URL, so a
    failed sign-up would be attempted twice.

    The redirect goes to the *referring* page, falling back to the form's own
    URL. Inertia's client follows the redirect, and the errors are read out of
    the session by the shared prop while that next page renders — which is
    also what clears them, so they do not reappear later.
    """
    flash(request, "errors", errors)
    from sillo_inertia import back

    return back(fallback=fallback)


async def _payload(request: Request) -> dict[str, Any]:
    """Read the submitted fields, whichever way they arrived.

    Inertia's client posts JSON. A plain HTML form — the no-JavaScript
    fallback, and what `curl -d` sends — posts urlencoded fields. Accepting
    both means the routes work before the front end has booted.
    """
    # `json` and `form` are async *properties*, not methods — awaited without
    # parentheses. `await request.json()` calls the coroutine the property
    # returns, which raises TypeError and leaves a "coroutine was never
    # awaited" warning as the only clue.
    content_type = (request.content_type or "").lower()
    if "application/json" in content_type:
        try:
            return dict(await request.json)
        except Exception:
            # A malformed body is a validation failure, not a 500. Falling
            # through to an empty mapping lets the field checks report it.
            return {}

    form = await request.form
    return {key: form.get(key) for key in form}
