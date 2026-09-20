"""Database wiring.

One definition of how this project connects, shared by the running
application, the migration commands, and anything else that opens the
database. Nothing here describes the connection twice, so the application and
its migrations cannot drift apart.
"""

from __future__ import annotations

from sillo.record import DatabaseConfig, DatabaseManager

from app.config import config

#: Modules scanned for models.
#:
#: A model that is not imported in ``database/models/__init__.py`` is invisible
#: to the ORM, and its first query fails with "default_connection cannot be
#: None" rather than anything about the import.
#:
#: Do not add ``sillo.users`` here. Models are keyed by class name, so the
#: framework's built-in ``User`` would displace this project's own and the
#: extra columns would silently stop being created.
MODEL_MODULES = ["database.models"]

#: Where migrations live, as a dotted path.
MIGRATIONS_MODULE = "database.migrations"


def database_config() -> DatabaseConfig:
    """The connection settings for this project."""
    return DatabaseConfig(
        url=config.database_url,
        pool_size=config.db_pool_size,
        echo=config.db_echo,
        generate_schemas=config.db_generate_schemas,
    )


def database() -> DatabaseManager:
    """A manager for this project's database.

    What a script that needs the ORM outside a request opens::

        async with database() as db:
            await User.all()

    The application does not call this — ``setup_record`` in
    ``app/bootstrap.py`` builds its own from the same :func:`database_config`
    and ties it to the application's startup and shutdown.
    """
    manager = DatabaseManager(database_config())
    manager.register_models(*MODEL_MODULES).set_migrations(MIGRATIONS_MODULE)
    return manager
