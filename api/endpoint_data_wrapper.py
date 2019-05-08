import requests

from api import description_parser
from api.models import EndpointSelect
from api.utils import replace_query_path, HttpHeaders, replace_query_params


class _EndpointDataWrapper:
    def __init__(self, type, endpoint: EndpointSelect):
        self.endpoint = endpoint
        self._parameters = sorted(self.endpoint.parameters.items())
        self.type = type
        self.endpoint_data = {}

    def _selection_key(self, data):
        key = [
            (name, data[field])
            for name, field in self._parameters
        ]
        return tuple(key)

    def load_for(self, data, request):
        url = request.build_absolute_uri()
        key_set = set([self._selection_key(row) for row in data])

        # fixme: need to rewrite this
        endpoint_path = f'/api/{self.type}/{self.endpoint.select_from.name}/'
        endpoint_url = replace_query_path(url, endpoint_path)

        headers = HttpHeaders(request.META).headers

        for key in key_set:
            value = self._get_all_pages_data(replace_query_params(endpoint_url, dict(key)), headers)
            self.endpoint_data[key] = value

        return self.endpoint_data

    def get_data(self, data):
        key = self._selection_key(data)
        return self.endpoint_data[key]

    def _get_all_pages_data(self, url, headers):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = []
        if self.type == 'json':
            while True:
                response_data = response.json()
                result += response_data['data']
                if not response_data['has_next']: break
                response = requests.get(response_data['next'], headers)
                response.raise_for_status()
        else:
            response_data = response.text
            # todo: implement for other types (XML)

        return result


class EndpointSelectWrapper:
    def __init__(self, type, endpoints):
        self.endpoints_data_wrappers = {
            endpoint_select.select_from.name: _EndpointDataWrapper(type, endpoint_select)
            for endpoint_select in endpoints
        }

    def load(self, data, request):
        for data_wrapper in self.endpoints_data_wrappers.values():
            data_wrapper.load_for(data, request)

    def get_data(self, select_item: description_parser.Select, data: dict):
        data_wrapper = self.endpoints_data_wrappers[select_item.endpoint_name.lower()]
        return data_wrapper.get_data(data)
