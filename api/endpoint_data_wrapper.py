import requests

from api import description_parser
from api.models import EndpointSelect, Endpoint
from api.utils import HttpHeaders, XMLNamedNode, BuilderTypeSelector
from api.utils import replace_query_path, replace_query_params


class _EndpointDependency:
    def __init__(self, filed_name, endpoint, children):
        self.endpoint = endpoint
        self.filed_name = filed_name
        self.children = children


def _get_endpoints_recursively(endpoint: Endpoint, name=None):
    children = endpoint.endpoint_selects.prefetch_related('select_from').all()
    children = [
        _get_endpoints_recursively(select.select_from, select.select_to_field_name)
        for select in children
    ]
    children = {it.filed_name: it for it in children}
    if name is not None:
        return _EndpointDependency(name, endpoint, children)
    return {None: _EndpointDependency(name, endpoint, children)}


def _rebuild_xml_result(root, parent_key, endpoint_dependency):
    if isinstance(root, dict):
        return {
            key: _rebuild_xml_result(value, key, endpoint_dependency)
            for key, value in root.items()
        }
    elif isinstance(root, (list, tuple)):
        endpoint = endpoint_dependency[parent_key]
        data = [
            _rebuild_xml_result(it, None, endpoint.children)
            for it in root
        ]
        return XMLNamedNode(data, endpoint.endpoint.name)
    else:
        return root


class _EndpointDataResultBuilder(BuilderTypeSelector):

    def build_json(self, data, *args, **kwargs):
        return data

    def build_xml(self, data, endpoint: Endpoint):
        dependency = _get_endpoints_recursively(endpoint)
        return _rebuild_xml_result(data, None, dependency)


class _EndpointDataWrapper:
    def __init__(self, type, endpoint: EndpointSelect):
        self._endpoint = endpoint
        self._name = self._endpoint.select_from.name
        self._parameters = sorted(self._endpoint.parameters.items())
        self._type = type
        self._endpoint_data = {}

    def _selection_key(self, data):
        key = [
            (name, data[field])
            for name, field in self._parameters
        ]
        return tuple(key)

    def load_for(self, data, request):
        url = request.build_absolute_uri()
        key_set = set([self._selection_key(row) for row in data])

        endpoint_path = f'/api/json/{self._name}/'
        endpoint_url = replace_query_path(url, endpoint_path)

        headers = HttpHeaders(request.META).headers

        for key in key_set:
            value = self._get_all_pages_data(replace_query_params(endpoint_url, dict(key)), headers)
            self._endpoint_data[key] = value

    def get_data(self, data):
        key = self._selection_key(data)
        return self._endpoint_data[key]

    def _get_all_pages_data(self, url, headers):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = []
        while True:
            response_data = response.json()
            result += response_data['data']
            if not response_data['has_next']: break
            response = requests.get(response_data['next'], headers=headers)
            response.raise_for_status()

        return _EndpointDataResultBuilder(self._type).build(result, self._endpoint.select_from)


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
        data_wrapper = self.endpoints_data_wrappers[select_item.endpoint_name]
        return data_wrapper.get_data(data)
