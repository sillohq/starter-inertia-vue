# Every task this project needs, discoverable with `make` on its own.
#
# The commands are plain uvicorn/npm/sillo invocations rather than anything
# bespoke, so you can read what a target does and run it by hand when you need
# to vary it.

.DEFAULT_GOAL := help
.PHONY: help setup install migrate migration plan rollback admin users \
        dev serve build typecheck test lint format check clean

PY   := uv run
APP  := app.main:app
HOST ?= 127.0.0.1
PORT ?= 8000

help:  ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

# -- setup -------------------------------------------------------------

# The placeholder key is replaced rather than copied: a starter whose
# SECRET_KEY is the same in every clone signs every deployment's sessions and
# CSRF tokens with a published secret.
setup: install ## Install everything, create .env, and set the database up
	@test -f .env || (cp .env.example .env \
	  && $(PY) python -c "import pathlib, secrets; p = pathlib.Path('.env'); p.write_text(p.read_text().replace('generate-me', secrets.token_urlsafe(48)))" \
	  && echo "  created .env with a fresh SECRET_KEY")
	@$(MAKE) migrate
	@echo "  ready. run 'make dev' in one terminal and 'npm run dev' in another."

install:  ## Install Python and Node dependencies
	uv sync --all-extras
	npm install

# -- database ----------------------------------------------------------

# Everything goes through the `sillo` command, which finds the application and
# derives its commands from it.
CONSOLE := $(PY) sillo

# The bootstrap on the first line is what makes this work on a fresh clone,
# where there is no migration to apply yet. It only runs when the migrations
# package is empty, so a later `make migrate` never writes one behind your back.
migrate:  ## Create the database and apply every pending migration
	@ls database/migrations/0*.py >/dev/null 2>&1 || ($(CONSOLE) db:init && $(CONSOLE) db:make initial)
	$(CONSOLE) db:migrate

migration:  ## Write a migration and apply it. make migration m="add_posts"
	$(CONSOLE) db:make "$(or $(m),update)" --apply

plan:  ## Show which migrations would run
	$(CONSOLE) db:plan

rollback:  ## Roll back to a migration. make rollback to=0001_initial
	@test -n "$(to)" || (echo "  need a target: make rollback to=0001_initial"; exit 1)
	$(CONSOLE) db:rollback "$(to)"

admin:  ## Create an administrator account. make admin e=ada@x.com u=ada
	@test -n "$(e)" -a -n "$(u)" || (echo "  need both: make admin e=ada@x.com u=ada"; exit 1)
	$(CONSOLE) user:admin "$(e)" "$(u)"

users:  ## List users
	$(CONSOLE) user:list

# -- running -----------------------------------------------------------

# Two processes, deliberately. Running Vite from the Makefile would hide which
# one printed an error, and you want the HMR output where you can see it.
dev:  ## Run the application with reload. Run `npm run dev` alongside it.
	@echo "  remember: npm run dev, in another terminal (VITE_DEV=true)"
	$(CONSOLE) serve --reload --host $(HOST) --port $(PORT)

serve:  ## Run as it would run in production. Needs `make build` and VITE_DEV=false.
	$(PY) uvicorn $(APP) --host 0.0.0.0 --port $(PORT) --workers 4

build:  ## Compile the front end into static/build
	npm run build

# -- quality -----------------------------------------------------------

test:  ## Run the Python test suite
	$(PY) pytest -q

typecheck:  ## Type-check the front end
	npm run typecheck

lint:  ## Check formatting and lint rules
	$(PY) ruff check .
	$(PY) ruff format --check .

format:  ## Apply formatting and fixable lint rules
	$(PY) ruff format .
	$(PY) ruff check --fix .

# `build` before `test` on purpose: the production-asset tests skip themselves
# when there is nothing built, and a check that silently skips its most
# fragile assertions is not a check.
check: lint typecheck build test  ## Everything CI runs

clean:  ## Remove caches and build artefacts
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache static/build dist build *.egg-info
