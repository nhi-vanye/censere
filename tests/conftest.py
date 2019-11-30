import logging
import pytest

import peewee

from playhouse.sqlite_ext import SqliteExtDatabase

test_db = SqliteExtDatabase(':memory:')
peewee_logger = logging.getLogger('peewee')
peewee_logger.addHandler(logging.StreamHandler())
peewee_logger.setLevel(logging.INFO)

import censere.models.triggers as TRIGGERS
import censere.models.functions as FUNC

FUNC.register_all( test_db )

@pytest.fixture(scope="module")
def database():
    global test_db

    return test_db

