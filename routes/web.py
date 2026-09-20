"""Inertia pages.

A handler names a component and returns its props. Whether that becomes a full
HTML document or a JSON page object is the adapter's decision, made from the
request — the first visit is a browser navigation and gets HTML, everything
after it is an XHR and gets JSON.

``render`` is imported from ``sillo_inertia`` rather than off an adapter
object. It finds the adapter through the middleware handling the request,
which is what lets this module stay free of any import back into ``app/``.
"""

from __future__ import annotations

from sillo.core.http import Request, Response
from sillo_inertia import redirect, render


async def home(request: Request, response: Response):
    """The landing page."""
    return await render(
        "Home",
        {
            "message": "Sillo on the back, Inertia and React on the front.",
        },
    )


async def dashboard(request: Request, response: Response):
    """A page only a signed-in user may see.

    The guard is written out rather than delegated to a decorator because what
    it should do is application-specific: an Inertia app redirects to the login
    page, where a JSON API would answer 401. Sillo's ``auth=`` route argument
    does the latter, and a 401 to Inertia's client surfaces as an unhandled
    error modal rather than a login screen.
    """
    if not request.user.is_authenticated:
        return redirect("/login")

    return await render(
        "Dashboard",
        {
            # Shared props already carry the signed-in user; this is the page's
            # own data. Anything expensive belongs behind `lazy()` so a partial
            # reload that does not ask for it does not pay for it.
            "stats": {
                "signed_in_as": request.user.email,
            },
        },
    )
