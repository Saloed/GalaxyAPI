from api.models import SchemaEntry


class ParamDescription:
    def __init__(self, name: str, condition: str, required: bool = False):
        self.name = name
        self.condition = condition
        self.required = required


class RequiredParamDescription:
    def __init__(self, name: str):
        self.name = name


class Custom:
    def __init__(self, name, condition, required=False):
        self.name = name
        self.condition = condition
        self.required = required

    def convert_to_description(self):
        return ParamDescription(self.name, self.condition, self.required)


class Exact:
    def __init__(self, name, condition, required=False):
        equals_pattern = ' = %s'
        self.name = name
        self.condition = condition + equals_pattern
        self.required = required

    def convert_to_description(self):
        return ParamDescription(self.name, self.condition, self.required)


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
                    entry = FieldEntryDescription(SchemaEntry.DB, key, value.name, value.type.__name__, cur_level)
                    entries.append(entry)
                elif isinstance(value, Select):
                    value.field_name = key
                    entry = FieldEntryDescription(SchemaEntry.SELECT, key, value.endpoint_name, None, cur_level)
                    entries.append(entry)
                    selects.append(value)
                elif isinstance(value, dict):
                    entry = FieldEntryDescription(SchemaEntry.NESTED, key, None, None, cur_level)
                    entries.append(entry)
                    parse_field_to_entry(value, entries, selects, cur_level + 1)
                else:
                    entry = FieldEntryDescription(SchemaEntry.NORMAL, key, None, value.__name__, cur_level)
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
                    self.params_description.append(param.convert_to_description())
                else:
                    raise ValueError("Illegal type in description params")

    def parse_req_params(self):
        if self.required_params:
            for param in self.required_params:
                self.required_params_description.append(RequiredParamDescription(param))
