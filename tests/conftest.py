import pytest

import peewee

test_db = peewee.SqliteDatabase(':memory:')

import censere.models.triggers as TRIGGERS

@pytest.fixture(scope="module")
def database():
    global test_db

    return test_db

