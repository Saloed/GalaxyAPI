import json
from django.test import Client
from jsonschema import validate
from api.views import *

def test_valid_schema_stipendia():
    client = Client()
    response = client.get('/api/json/ping/')
    print(response.content )
    schema = json.load(open("tests/pingpong.json"))
    validate(json.loads(response.content) , schema)
