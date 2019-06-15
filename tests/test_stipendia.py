import json
from django.test import Client
from jsonschema import validate
from api.views import *

def test_valid_schema_students():
    client = Client()
    response = client.get('api/json/students?id=1')
    print(response.content )
    schema = json.load(open("tests/student_schema.json"))
    validate(json.loads(response.content) , schema)
