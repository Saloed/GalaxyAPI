import pytest


@pytest.fixture(scope='session')
def django_db_setup():
    """Avoid creating/setting up the test database"""
    pass
