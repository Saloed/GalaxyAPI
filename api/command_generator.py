# TODO: hochu takoi interface
# class Description:
#     fields
#     required_params
#     params


class CommandGenerator:
    fields = []
    required_params = []
    params = []

    def __init__(self, description, sql):
        # TODO: we need django log or something
        print('Init parser with params', description, sql)
        self.description = description
        self.fields = description.fields
        self.required_params=description.required_params
        self.params = description.params
        self.sql = sql
        self.validate()

    def validate(self):
        # TODO: implementation if needed
        return True

    def run(self, cursor, param_values):
        if len(self.required_params) != 0:
            cursor.execute(self.sql, param_values)
        else:
            cursor.execute(self.sql)
        raw_data = cursor.fetchall()
        return self.convert_to_result(raw_data)

    def reduce_entry(self, i, entry):
        pass

    def convert_to_result(self, raw_data):
        res = []
        for entry in raw_data:
            res_entry = {}
            for i in range(len(entry)):
                field = list(self.fields.keys())[i]
                if field == 'select':
                    print("create new generator and run it")
                    # TODO create new generator with class name?
                    pass
                elif field == 'db':
                    # TODO hz cheita
                    pass
                elif field == {}:
                    print("field is dict")
                    pass
                else:
                    res_entry[field] = entry[i]
                    print("field is primitive something")
            res.append(res_entry)
        return res