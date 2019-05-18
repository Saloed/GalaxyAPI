import requests

from django.conf import settings

from api.models import EndpointSelect
from api.utils import replace_query_path, http_headers, replace_query_params


class _EndpointDataWrapper:
    def __init__(self, endpoint: EndpointSelect):
        self.endpoint = endpoint
        self._parameters = sorted(self.endpoint.parameters.items())
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

        endpoint_path = f'{settings.API_PATH_PREFIX}/{self.endpoint.select_from.name}'
        endpoint_url = replace_query_path(url, endpoint_path)
        endpoint_url = replace_query_params(endpoint_url, {'format': 'json'})

        headers = http_headers(request)
        headers['Accept'] = 'application/json'

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
        while True:
            response_data = response.json()
            result += response_data['data']
            if not response_data['has_next']: break
            response = requests.get(response_data['next'], headers)
            response.raise_for_status()

        return result


class EndpointSelectWrapper:
    def __init__(self, endpoints):
        self.endpoints_data_wrappers = {
            endpoint_select.select_from.name: _EndpointDataWrapper(endpoint_select)
            for endpoint_select in endpoints
        }

    def load(self, data, request):
        for data_wrapper in self.endpoints_data_wrappers.values():
            data_wrapper.load_for(data, request)

    def get_data(self, endpoint_name, data: dict):
        data_wrapper = self.endpoints_data_wrappers[endpoint_name]
        return data_wrapper.get_data(data)
