# Sillo + Inertia + React

A starting point for applications that want a server that owns the data and a
React front end that owns the interface, with no API between them.

A handler names a component and returns its props:

```python
async def dashboard(request: Request, response: Response):
    if not request.user.is_authenticated:
        return redirect("/login")

    return await render("Dashboard", {"stats": {"signed_in_as": request.user.email}})
```

The component receives them as props. There is no endpoint to define, no
client-side fetch, no loading state, and no second description of the same
data.

```tsx
export default function Dashboard({ stats }: Props) {
  return <p>Signed in as {stats.signed_in_as}</p>
}
```

## What is in the box

- **Sillo** with the Record ORM, sessions, CSRF and CORS wired in a deliberate
  order
- **Inertia** through [`sillo-inertia`](https://github.com/sillohq/inertia)
- **React 19 + TypeScript + Vite**, with hot module replacement in development
  and a hashed, manifest-driven build for production
- **Sign up, sign in, sign out**, with server-side validation whose errors
  render on the form the Inertia way
- **A persistent layout**, shared props, and flash messages
- **52 Python tests** covering the Inertia protocol, the auth flow, CSRF and
  the production asset path

## Getting started

```bash
make setup      # installs Python and Node deps, writes .env, creates the database
make dev        # the application, with reload
npm run dev     # the Vite dev server — in a second terminal
```

Then open <http://127.0.0.1:8000>.

Both processes are needed in development. The page loads its JavaScript from
Vite, so with only `make dev` running you get a blank page and a console full
of failed module requests.

## How it fits together

```
app/
  config.py       typed settings, loaded from .env
  inertia.py      the adapter, shared props, and the flash helpers
  bootstrap.py    middleware order, database, static, routes
routes/
  web.py          pages
  auth.py         sign up / sign in / sign out
  api.py          the small JSON surface that is not Inertia
root.html         the HTML shell, with the Inertia placeholders
js/
  main.tsx        createInertiaApp, and the page resolver
  app.css         Tailwind entry and the design tokens
  ui.ts           class strings shared across pages
  types.ts        the shape of the shared props
views/
  Layout.tsx      the shell every page renders inside
  pages/          one component per page name a handler can return
database/
  models/user.py  the single user model
```

### The two shapes of a response

The same URL answers two ways, and which one you get is decided by a request
header rather than by your code:

| Request | Response |
| --- | --- |
| A browser navigation | The full HTML document, with the page object embedded |
| An Inertia visit (`X-Inertia: true`) | The page object as JSON |

Almost every confusing bug in an Inertia application is a confusion about
which of those is happening. `tests/test_pages.py` pins both.

### Validation errors

Inertia has no way to return a validation error from a POST directly. A failed
submission redirects **back**, and the errors have to survive that redirect —
so they go into the session, and a shared prop reads them out on the next
render:

```python
# routes/auth.py
if errors:
    return back_with_errors(request, errors, "/login")
```

```tsx
// The `errors` object useForm gives you is that shared prop.
{errors.email && <em className="field__error">{errors.email}</em>}
```

Reading is destructive, which is what makes it a flash: the errors appear on
the page you land on and are gone by the next one.

### CSRF

Unsafe methods need a token. Inertia's client is axios, which attaches one
automatically — but only under its own convention: it reads the `XSRF-TOKEN`
cookie and sends `X-XSRF-TOKEN`. Sillo's defaults are `csrftoken` and
`X-CSRFToken`, so `app/bootstrap.py` renames them to match. Without that every
form submission is a 403 and nothing on either side says why.

That cookie is deliberately **not** `httponly`, because axios cannot read a
cookie the browser hides from JavaScript. It is safe because the token is
useless without the session cookie, which stays `httponly`.

### Development and production assets

| | `VITE_DEV=true` | `VITE_DEV=false` |
| --- | --- | --- |
| Scripts come from | the Vite dev server | `static/build`, via the manifest |
| Needs | `npm run dev` | `npm run build` |
| Filenames | source paths | content-hashed |

One string has to agree in three places: `js/main.tsx` is the input in
`vite.config.ts`, the `ENTRY` constant in `app/inertia.py`, and the key Vite
writes into the manifest. When they drift, development still works and
production renders a page with no JavaScript at all — which is why
`tests/test_production_assets.py` asserts it.

## Deploying

```bash
npm run build
VITE_DEV=false ASSET_VERSION=$(git rev-parse --short HEAD) make serve
```

Set `ASSET_VERSION` to something that changes per build. When it changes, an
Inertia visit from a client on the old bundle gets a 409 and does a full
reload — which is what stops a stale front end from talking to a new backend.

Put nginx or Caddy in front and serve `static/build/assets` at `/assets`
directly; the application's own static mount then never sees traffic.

## Adding a page

1. Write the handler in `routes/web.py` and return `render("Reports/Index", {...})`.
2. Register it in `app/bootstrap.py` with `exclude_from_schema=True` — pages
   are not an API and should not be documented as one.
3. Create `views/pages/Reports/Index.tsx` with a default export.

The resolver in `js/main.tsx` maps the name to the file. A name with no matching
file raises an error that says which file it expected, rather than the
`Cannot read properties of undefined` you would otherwise get.

## Commands

Run `make` on its own for the full list. The ones you will use:

| | |
| --- | --- |
| `make dev` | the application, with reload |
| `npm run dev` | the Vite dev server |
| `make test` | the Python suite |
| `make check` | everything CI runs |
| `make migration m="add_posts"` | write and apply a migration |
| `make admin e=ada@x.com u=ada` | create an administrator |

## Notes

The database is SQLite so that `make setup` works with nothing else installed.
Point `DATABASE_URL` at Postgres and swap `aiosqlite` for `asyncpg` in
`pyproject.toml` when you outgrow it.

There is no admin panel here, unlike [the standard
starter](https://github.com/sillohq/starter). Adding one means adding
`sillo.admin.models` to `MODEL_MODULES` and mounting the site *before* the
middleware block — the admin attaches its own session-reading middleware, so
registering it after leaves the session middleware inside it and every admin
page 500s.
