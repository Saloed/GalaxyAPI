from typing import List

from api.endpoint import Select
from api.endpoint_loader import EndpointStorage


class _EndpointDataWrapper:
    def __init__(self, select_from_endpoint: Select):
        self.select_from_endpoint = select_from_endpoint
        self._endpoint = EndpointStorage.endpoints[select_from_endpoint.endpoint]
        self._parameters = sorted(self.select_from_endpoint.params.items())
        self.endpoint_data = {}

    def _selection_key(self, data):
        key = [
            (name, data[field])
            for name, field in self._parameters
        ]
        return tuple(key)

    def load_for(self, data):
        from api.endpoint_processor import EndpointProcessor
        processor = EndpointProcessor(self._endpoint)

        key_set = set([self._selection_key(row) for row in data])
        for key in key_set:
            value = processor.process(dict(key), request=None, disable_pagination=True)
            self.endpoint_data[key] = value

        return self.endpoint_data

    def get_data(self, data):
        key = self._selection_key(data)
        return self.endpoint_data[key]


class EndpointSelectWrapper:
    def __init__(self, endpoints: List[Select]):
        self.endpoints_data_wrappers = {
            endpoint_select.endpoint: _EndpointDataWrapper(endpoint_select)
            for endpoint_select in endpoints
        }

    def load(self, data):
        for data_wrapper in self.endpoints_data_wrappers.values():
            data_wrapper.load_for(data)

    def get_data(self, endpoint_name, data: dict):
        data_wrapper = self.endpoints_data_wrappers[endpoint_name]
        return data_wrapper.get_data(data)
