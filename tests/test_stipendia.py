import json
from django.test import RequestFactory
from jsonschema import validate
from api.views import *

def test_valid_schema_stipendia():
    rf=RequestFactory()
    args={'type':'json','endpoint':'ping'}
    request=rf.get('/')
    d=DispatchView()
    resp = d.get(request,type="json",endpoint='ping')
    schema = json.load(open("tests/pingpong.json"))
    validate(json.loads(resp.content) , schema)

if __name__ =="__main__":
    print (test_valid_schema_stipendia())
