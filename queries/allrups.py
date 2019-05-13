class Rup:
    sql = 'allrups.sql'
    pagination_key = 'ID'
    fields = {
        'ID': str,
        'Status': {
            'ID': Db('Status_ID', str),
            'NAME': Db('Name', str)
        }
    }
