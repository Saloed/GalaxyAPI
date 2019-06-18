import os
import builtins
import inspect
from collections import OrderedDict

import yaml


class RequiredParamDescription:
    def __init__(self, name: str):
        self.name = name


class Custom:
    def __init__(self, name, condition, required=False):
        self.name = name
        self.condition = condition
        self.required = required


class Exact:
    def __init__(self, name, condition, required=False):
        equals_pattern = ' = %s'
        self.name = name
        self.condition = condition + equals_pattern
        self.required = required


class Select:
    def __init__(self, endpoint_name, **required_params):
        self.endpoint_name = endpoint_name
        self.required_params = required_params
        self.field_name = None


class Db:
    def __init__(self, name, type):
        self.name = name
        self.type = type


DESCRIPTION_CALLS = [
    Custom,
    Exact,
    Db,
    Select
]


class FieldEntryDescription:
    def __init__(self, entry_type, name, value, type, level):
        """
        :param entry_type: type of entry: one of Nested, Db, Select, Normal
        :param name: field name
        :param value: in case of Select type used to store endpoint_name,
                      in case DB used to store db_name
                      otherwise None
        :param type:  field type. In case of Select and Nested is None
        :param level: field level
        """
        self.entry_type = entry_type
        self.field_name = name
        self.value = value
        self.type = type
        self.level = level


NESTED = 'Nested'
DB = 'Db'
SELECT = 'Select'
NORMAL = 'Normal'


class DescriptionParser:

    def __init__(self, description):
        self.description = description
        self.name = description.__name__
        self.pagination_key = description.pagination_key
        self.sql = description.sql
        self.fields = getattr(description, 'fields')
        self.required_params = getattr(description, 'required_params', [])
        self.params = getattr(description, 'params', [])
        self.fields_description = []
        self.params_description = []
        self.required_params_description = []
        self.selects_description = []
        self.validate()

    def validate(self):
        pass

    def parse(self):
        self.parse_fields()
        self.parse_params()
        self.parse_req_params()

    def parse_fields(self):
        def parse_field_to_entry(root, entries, selects, cur_level):
            for key, value in root.items():
                if isinstance(value, Db):
                    entry = FieldEntryDescription(DB, key, value.name, value.type.__name__, cur_level)
                    entries.append(entry)
                elif isinstance(value, Select):
                    value.field_name = key
                    entry = FieldEntryDescription(SELECT, key, value.endpoint_name, None, cur_level)
                    entries.append(entry)
                    selects.append(value)
                elif isinstance(value, dict):
                    entry = FieldEntryDescription(NESTED, key, None, None, cur_level)
                    entries.append(entry)
                    parse_field_to_entry(value, entries, selects, cur_level + 1)
                else:
                    entry = FieldEntryDescription(NORMAL, key, None, value.__name__, cur_level)
                    entries.append(entry)
            return entries, selects

        if self.fields:
            self.fields_description, self.selects_description = parse_field_to_entry(self.fields, [], [], 0)
        else:
            raise ValueError(f'Empty fields in Description class: {self.description}')

    def parse_params(self):
        if self.params:
            for param in self.params:
                if isinstance(param, Custom) or isinstance(param, Exact):
                    self.params_description.append(param)
                else:
                    raise ValueError("Illegal type in description params")

    def parse_req_params(self):
        if self.required_params:
            for param in self.required_params:
                self.required_params_description.append(RequiredParamDescription(param))


def load_descriptions():
    files = (
        os.path.join('queries', file)
        for file in os.listdir('queries')
    )
    files = [file for file in files if os.path.isfile(file) and file.endswith('.py')]
    description_lines = []
    for file in files:
        with open(file) as f:
            description_lines += f.readlines()

    description_text = ''.join(description_lines)
    context = {call.__name__: call for call in DESCRIPTION_CALLS}
    context['__builtins__'] = builtins
    definitions = dict()
    exec(description_text, context, definitions)
    descriptions = [
        definition
        for definition in definitions.values()
        if inspect.isclass(definition)
    ]
    return descriptions


def parse_descriptions(descriptions):
    description_parsers = [

        DescriptionParser(description)
        for description in descriptions
    ]
    for parser in description_parsers:
        parser.parse()

    for parser, desc in zip(description_parsers, descriptions):
        parser.original_schema = desc.fields

    return description_parsers


def to_new_format_params(param):
    return {
        'name': param.name,
        'type': 'string',
        'operation': 'exact' if isinstance(param, Exact) else 'custom',
        'condition': param.condition,
        'required': param.required,
        'description': '',
        'default': '',
        'example': ''
    }


def to_new_format_required_params(i, param):
    return {
        'name': param.name,
        'type': 'string',
        'position': i,
        'description': '',
        'default': '',
        'example': ''
    }


def to_new_format_schema_type(_type):
    return {
        'str': 'string',
        'int': 'integer'
    }.get(_type, 'string')


def to_new_format_schema(schema, parent_key):
    if isinstance(schema, dict):
        return {
            'type': 'object',
            'name': '',
            'description': '',
            'fields': {
                key: to_new_format_schema(value, key)
                for key, value in schema.items()
            }
        }
    elif isinstance(schema, list):
        raise Exception('List is not supported')
    elif isinstance(schema, Select):
        return {
            'type': 'select',
            'endpoint': schema.endpoint_name,
            'params': schema.required_params,
            'description': ''
        }
    elif isinstance(schema, Db):
        return {
            'type': to_new_format_schema_type(schema.type),
            'db_name': schema.name,
            'description': '',
            'example': ''
        }
    else:
        return {
            'type': to_new_format_schema_type(schema),
            'db_name': parent_key,
            'description': '',
            'example': ''
        }


def to_new_format(description):
    name = description.name
    sql = description.sql
    pagination_key = description.pagination_key
    sql_params = [to_new_format_required_params(i, it) for i, it in enumerate(description.required_params_description)]
    params = [to_new_format_params(it) for it in description.params_description]
    schema = to_new_format_schema(description.original_schema, None)
    return {
        'name': name,
        'description': '',
        'sql': sql,
        'pagination_enabled': pagination_key is not None,
        'aggregation_enabled': False,
        'key': pagination_key,
        'sql_params': sql_params,
        'params': params,
        'schema': schema
    }


def save_yaml(description):
    with open(f"queries/{description['name']}.yaml", 'w') as f:
        yaml.dump(description, f, default_flow_style=False, sort_keys=False)


def process():
    descriptions = load_descriptions()
    descriptions = parse_descriptions(descriptions)
    descriptions = [to_new_format(it) for it in descriptions]
    for description in descriptions:
        save_yaml(description)


if __name__ == '__main__':
    process()
