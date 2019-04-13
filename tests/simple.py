import pytest
from django.db import connections


@pytest.mark.django_db
def test_db_connection():
    with connections['galaxy_db'].cursor() as cursor:
        cursor.execute('SELECT Name FROM sys.Tables')
        tables = cursor.fetchall()
    assert len(tables) > 0
