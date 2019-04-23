# this file is for util functions for description_parser

import os

def test_import():
    print("test import is works!")


# TODO: discuss how migrations and running of sql queries will be hold
def run_sql_with_params(cursor, sql_filename, params):
    file_path = os.path.join(os.path.dirname(__file__), sql_filename)
    sql_statement = open(file_path).read()
    cursor.execute(sql_statement, params)
    return cursor.fetchall()


def get_sql_from_file(sql_filename):
    file_path = os.path.join(os.path.dirname(__file__), sql_filename)
    return open(file_path).read()

# TODO db('ID', int)
# TODO select()
