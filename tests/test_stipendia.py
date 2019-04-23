import json
import requests
from jsonschema import validate


def test_valid_schema_stipendia():
    #json_data = json.load(open("stipends.ex.json"))
    t=requests.get("http://localhost:8080/stipends.ex.json")
    schema = json.load(open("stipendia.json"))
    validate(t.json() , schema)

if __name__ =="__main__":
    print (test_valid_schema_stipendia())
