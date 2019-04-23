class Fins:
    """
    Данный endpoint просто выполняет SQL запрос и не поддерживает фильтрацию.
    SQL должен содержать поля CODE, ID и NAME, которые возвращает endpoint.
    Указание типов в описании необходимо для дальнейшего их использования при генерации документаци
    Пример ответа в формате JSON:
    [
        {
            'CODE': 12345,
            'ID': 1,
            'NAME': 'some random name'
        }
    ]


    """
    params = []
    required_params = []
    fields = {
        'CODE': int,
        'ID': int,
        'NAME': str
    }
