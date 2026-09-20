"""Application assembly.

``create_app`` is the single place where the application is put together:
middleware, then infrastructure, then routes. Keeping it a function rather than
module-level code means tests can build an isolated instance, and the import in
``app/main.py`` stays trivial.
"""

from __future__ import annotations

from sillo import SilloApp
from sillo.auth import AuthenticationMiddleware
from sillo.auth.session_auth import SessionAuthBackend
from sillo.record import setup_record
from sillo.security import CorsConfig, CORSMiddleware
from sillo.security.csrf import CSRFConfig, CSRFMiddleware
from sillo.session import SessionConfig, SessionMiddleware

from app.config import config, cors_origins
from app.inertia import BUILD_DIR, build_inertia, share_globals
from database.models.user import User


def create_app() -> SilloApp:
    """Build and return the configured application."""
    application = SilloApp(
        debug=config.debug,
        title=config.app_name,
        version="0.1.0",
    )

    _register_middleware(application)
    _register_database(application)
    _register_static(application)
    _register_routes(application)

    return application


def _register_middleware(application: SilloApp) -> None:
    """Attach middleware.

    ``application.use()`` builds the chain inside-out: whatever is registered
    *last* ends up outermost and therefore runs *first* on the way in. The
    registrations below are in reverse of the runtime order, which is

        CORS → session → CSRF → authentication → Inertia → handler.

    Each position is load-bearing:

    * Session is outside authentication because ``SessionAuthBackend`` reads
      ``request.session``. The other way round and every request logs
      "No Session Middleware Installed" and ``request.user`` is never set.
    * Inertia is innermost because route modules call the module-level
      ``render()``, which resolves the adapter from a context variable that
      only exists inside this middleware. Anything outside it renders fine;
      anything that needs the adapter must be within.
    * CSRF is outside authentication so a rejected token never reaches a
      database lookup.
    """
    inertia = build_inertia()
    share_globals(inertia)
    inertia.middleware(application)
    # Kept on the application so tests and handlers can reach the adapter
    # without importing the module that built it.
    application.state["inertia"] = inertia

    application.use(
        AuthenticationMiddleware(
            user_model=User,
            backend=SessionAuthBackend(),
        )
    )

    # Inertia's client is axios, which auto-attaches a CSRF header on unsafe
    # methods — but only under its own convention: it reads the `XSRF-TOKEN`
    # cookie and sends `X-XSRF-TOKEN`. Sillo's defaults are `csrftoken` and
    # `X-CSRFToken`, so left alone every POST from the front end is rejected
    # with 403 and nothing on either side explains why.
    #
    # Renaming here rather than configuring axios on the client keeps it in
    # one place, and matches what Laravel/Rails clients already expect.
    #
    # httponly is off for the same reason and only for this cookie: axios
    # cannot read a cookie the browser hides from JavaScript. That is safe
    # precisely because the token is useless without the session cookie, which
    # stays httponly — an attacker who can read the CSRF token still cannot
    # act as the user.
    application.use(
        CSRFMiddleware(
            config=CSRFConfig(
                enabled=True,
                cookie_name="XSRF-TOKEN",
                header_name="X-XSRF-TOKEN",
                cookie_httponly=False,
                cookie_secure=config.app_env != "local",
                secret_key=config.secret_key,
            )
        )
    )

    application.use(
        SessionMiddleware(
            config=SessionConfig(
                session_cookie_name=config.session_cookie_name,
                session_expiration_time=config.session_lifetime,
                # Secure cookies require HTTPS, which local development is not.
                # A `Secure` cookie over http is accepted by the browser and
                # then never sent back, which surfaces one request later as a
                # session that will not persist rather than as a cookie error.
                session_cookie_secure=config.app_env != "local",
            ),
            secret_key=config.secret_key,
        )
    )

    application.use(
        CORSMiddleware(
            config=CorsConfig(
                allow_origins=cors_origins(),
                allow_credentials=True,
            )
        )
    )


def _register_database(application: SilloApp) -> None:
    """Wire the Record ORM into the application lifecycle.

    ``setup_record`` registers the startup and shutdown hooks and the
    per-request context middleware, and stores the manager on
    ``application.state["record"]`` — which is what the health check reads and
    what the ``sillo`` command reaches for its migration commands.
    """
    from database.config import MIGRATIONS_MODULE, MODEL_MODULES, database_config

    manager = setup_record(application, database_config(), model_modules=MODEL_MODULES)
    manager.set_migrations(MIGRATIONS_MODULE)


def _register_static(application: SilloApp) -> None:
    """Serve the compiled front end.

    Only used when ``VITE_DEV=false``. In development every asset comes from
    the Vite dev server instead, and this mount is never hit.

    The mount point is ``/assets`` because that is what the adapter builds URLs
    against: it takes each file named in the Vite manifest, strips the leading
    ``assets/``, and prefixes ``asset_prefix``. So the directory served here has
    to be the ``assets`` folder *inside* the build output, not the build output
    itself — mount one level up and every script 404s with a manifest that is
    perfectly correct.

    Put nginx or Caddy in front in production and this never sees traffic.
    """
    from sillo.core.routing import Group
    from sillo.static import StaticFiles

    assets = BUILD_DIR / "assets"
    if not assets.is_dir():
        # Nothing built yet. Mounting a missing directory raises at startup,
        # which would make `npm run build` a prerequisite for running the tests
        # or the dev server — neither of which needs it.
        return

    application.add_route(Group(path="/assets", app=StaticFiles(directory=str(assets))))


def _register_routes(application: SilloApp) -> None:
    """Attach the application's routes.

    Order is significant. A router claims its whole prefix subtree, so the most
    specific prefix is mounted first.

    Pages are registered one at a time rather than as a router, because a
    ``Router`` with no prefix mounts at ``""`` and claims everything beneath it.
    """
    from routes.api import router as api_router  # /api

    application.mount_router(api_router)

    from routes import auth, web

    # `exclude_from_schema` on every page, because these are not an API and
    # documenting them as one is actively misleading: /docs would list a
    # `GET /login` returning "Successful Response" with a JSON content type,
    # when it returns an HTML document to a browser and a page object to
    # Inertia. The OpenAPI document should describe what other systems call.
    page = {"exclude_from_schema": True}

    application.get("/", handler=web.home, name="home", **page)
    application.get("/dashboard", handler=web.dashboard, name="dashboard", **page)

    application.get("/login", handler=auth.show_login, name="login", **page)
    application.post("/login", handler=auth.login, name="login.store", **page)
    application.get("/register", handler=auth.show_register, name="register", **page)
    application.post("/register", handler=auth.register, name="register.store", **page)
    application.post("/logout", handler=auth.logout, name="logout", **page)
