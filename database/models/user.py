"""The application's user model.

``sillo.users.UserBaseModel`` supplies the fields and behaviour authentication
depends on — email, username, hashed password, the active/staff/superuser
flags, and ``set_password``/``check_password``. Add your own columns here; the
inherited ones should not be redeclared.

Three constraints are worth knowing before editing this file:

* Only the modules listed in ``MODEL_MODULES`` (``database/config.py``) are
  registered with the ORM, and models are keyed by class name. Do not add
  ``sillo.users`` to that list — its built-in ``User`` would displace this one
  and the extra columns below would silently stop being created.
* ``password`` is redeclared, on purpose. See the note on the field.
* Tortoise does not call Django's ``contribute_to_class`` hook, so the manager
  is bound to this model explicitly at the bottom of the file.

Whatever you add here, remember that it is `current_user` in ``app/inertia.py``
that decides what reaches the browser — and it lists fields by hand precisely
so that a column added here does not start being published by accident.
"""

from __future__ import annotations

from sillo.record.fields import PasswordField
from sillo.users import UserBaseModel, UserManager
from tortoise import fields


class User(UserBaseModel):
    """Someone with an account."""

    #: Query helpers: ``User.objects.create_user(...)``, ``get_by_email(...)``.
    objects = UserManager()

    #: Declared, not inherited. ``UserBaseModel`` types this as a plain
    #: CharField, which stores exactly what it is handed — so
    #: ``user.password = "hunter2"`` followed by ``save()`` writes the
    #: plaintext, silently. ``PasswordField`` hashes on the way to the
    #: database.
    password = PasswordField()

    # Your own profile fields go here. Note that `display_name`, `identity`
    # and `is_authenticated` are read-only properties on the base class —
    # declaring a field with one of those names shadows the property and fails
    # on assignment.
    full_name = fields.CharField(max_length=150, null=True)

    class Meta:
        table = "users"

    def __str__(self) -> str:
        return self.email


# Bind the manager to this model. Without this the manager has no model and
# falls back to sillo's built-in User, which this project does not register —
# producing a confusing "default_connection cannot be None" at the first query.
User.objects.contribute_to_class(User, "objects")
