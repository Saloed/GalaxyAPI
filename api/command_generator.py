# TODO: hochu takoi interface
# class Description:
#     fields
#     required_params
#     params


class Select:
    pass


class CommandGenerator:
    fields = []
    required_params = []
    params = []

    def __init__(self, description, sql):
        # TODO: we need django log or something
        print('Init parser with params', description, sql)
        self.description = description
        self.fields = description.fields
        self.required_params = description.required_params
        self.params = description.params
        self.sql = sql
        self.validate()

    def validate(self):
        # TODO: implementation if needed
        return True

    def run(self, cursor, required_param_values):
        if len(self.required_params) != 0:
            cursor.execute(self.sql, required_param_values)
        else:
            cursor.execute(self.sql)
        raw_data = cursor.fetchall()
        return self.convert_to_result(raw_data)

    def reduce_entry(self, cur_fields, entry):
        res_entry = {}
        for i in range(len(entry)):
            field = list(cur_fields.keys())[i]
            field_type = cur_fields[list(cur_fields.keys())[i]]
            if isinstance(field_type, Select):
                print("create new generator and run it")
            #  TODO: here we need to determine a link between sql and description
            # and how in params values will ve introduced params for internal api calls
            # TODO: db is needed for description and support so we miss handle this case
            elif isinstance(field_type, dict):
                res_entry[field] = self.reduce_entry(field, entry[i])
                pass
            else:
                res_entry[field] = entry[i]
                print("field is primitive something")

        return res_entry

    def convert_to_result(self, raw_data):
        res = []
        for entry in raw_data:
            res_entry = self.reduce_entry(self.fields, entry)
            res.append(res_entry)
        return res
