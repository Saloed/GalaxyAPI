import json
from jsonschema import validate


def test_valid_schema_stipendia():
    json_data = json.load(open("stipends.ex.json"))
    schema = json.load(open("stipendia.json"))
    validate(json_data , schema)

if __name__ =="__main__":
    print (test_valid_schema_stipendia())
