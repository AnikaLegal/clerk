from importlib import import_module

import pytest
from django.db import connection

SECRET_TABLES = import_module(
    "accounts.migrations.0015_hide_secret_tables_from_readers"
).SECRET_TABLES


# Row-level security belongs to the table, so a later migration (ours or a
# package's) that drops and recreates one of these tables silently loses it,
# and read-only roles such as Retool's would see session keys and OAuth
# tokens again.
@pytest.mark.django_db
def test_secret_tables_have_row_level_security():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT relname FROM pg_class WHERE relrowsecurity AND relname = ANY(%s)",
            [SECRET_TABLES],
        )
        assert {row[0] for row in cursor.fetchall()} == set(SECRET_TABLES)
