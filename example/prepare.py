import os
import sys
from pymongo import MongoClient

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.extend([ROOT_PATH])
print("Make sure mongodb is running")


def drop_collection():
    db = MongoClient("mongodb://localhost")['simple_example_for_pymongokeyset']
    db.drop_collection('test_collect')


def get_collection():
    db = MongoClient("mongodb://localhost")['simple_example_for_pymongokeyset']
    return db['test_collect']


def prepare():
    drop_collection()
    collection = get_collection()
    return collection


# TODO build a HTTP server example. Maybe by web.py
