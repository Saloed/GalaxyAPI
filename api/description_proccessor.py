from api.query_execution import Param, RequiredParam


class Custom:
    def __init__(self, name, condition, required=False):
        self.name = name
        self.condition = condition
        self.required = required

    def convert_to_param(self):
        return Param(self.name, self.condition, self.required)


class Exact:
    def __init__(self, name, condition, required=False):
        self.name = name
        self.condition = condition
        self.required = required

    def convert_to_param(self):
        # TODO: probably add equals and input symbol for folloing execution
        # example: 'LoadPersons.F$wyeared' -> 'LoadPersons.F$wyeared = \''{}'\''
        return Param(self.name, self.condition, self.required)


class Select:
    def __init__(self, endpoint_name, req_param):
        self.endpoint_name = endpoint_name
        self.req_param = req_param


class FieldEntry:
    def __init__(self, name, db_name, type, level):
        self.name = name
        self.db_name = db_name
        self.type = type
        self.level = level


class Db:
    def __init__(self, name, type):
        self.name = name
        self.type = type


class Complex:
    def __init__(self, schema, aggregate):
        self.schema = schema
        self.aggregate = aggregate


class DescriptionProcessor:
    parsed_fields = []
    parsed_params = []
    parsed_req_params = []

    def __init__(self, description):
        self.description = description
        self.fields = getattr(description, 'fields')
        self.required_params = getattr(description, 'required_params', [])
        self.params = getattr(description, 'required_params', [])
        self.validate()
        self.parse()

    def validate(self):
        pass

    def parse(self):
        self.parse_fields()
        self.parse_params()
        self.parse_req_params()

    def parse_field_to_entry(self, root, entries, cur_level):
        for key in root.keys():
            self.log.debug(key)
            if isinstance(root[key], Db):
                entries.append(FieldEntry(key, root[key].name, 'Db', cur_level))
            elif isinstance(root[key], Select):
                entries.append(FieldEntry(key, key, 'Select', cur_level))
            elif isinstance(root[key], Complex):
                entries.append(FieldEntry(key, key, 'Complex', cur_level))
                # TODO: how to handle it some way as a dict
            elif isinstance(root[key], dict):
                entries.append(FieldEntry(key, key, 'dict', cur_level))
                self.parse_field_to_entry(root[key], entries, cur_level + 1)
            else:
                entries.append(FieldEntry(key, key, str(root[key]), cur_level))

        return entries

    def parse_fields(self):
        if self.fields:
            self.parsed_fields = self.parse_field_to_entry(self.fields, [], 0)
        else:
            raise ValueError(f'Empty fields in Description class: {self.description}')

    def parse_params(self):
        if self.params:
            for param in self.params:
                if isinstance(param, Custom) or isinstance(param, Exact):
                    self.parsed_params.append(param.convert_to_param())
                else:
                    raise ValueError("Illegal type in description params")

    def parse_req_params(self):
        if self.required_params:
            for param in self.required_params:
                self.parsed_req_params.append(RequiredParam(param))
