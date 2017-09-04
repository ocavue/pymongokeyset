import os
import sys
import unittest
from pymongo import MongoClient

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.extend([ROOT_PATH])


def get_collect_for_test():
    def get_db_name(client):
        for i in range(10000):
            db_name = 'test_db' + str(i)
            if db_name not in client.database_names():
                return db_name
        raise Exception("Can't find a empty db for test")

    client = MongoClient("mongodb://localhost")
    db_name = get_db_name(client)
    db = client[db_name]
    collect = db['test_collect']
    return collect


def drop_db_from_collect(collect):
    collect.database.client.drop_database(collect.database)


class BaseTestCase(unittest.TestCase):
    # Can't use mongomock here, beacause pymongokeyset use some private variables of pymongo.cursor.Cursor

    objs = []

    def setUp(self):
        self.collect = get_collect_for_test()
        self.collect.insert_many(self.objs)

        self.cursor = self.collect.find({}).sort([
            ('m', 1),
            ('n', 1),
            ('_id', 1),
        ])

    def tearDown(self):
        drop_db_from_collect(self.collect)
