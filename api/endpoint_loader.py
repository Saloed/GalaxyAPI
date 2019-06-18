import os
import yaml

from dacite import Config, from_dict

from django.conf import settings

from api.endpoint import *


def validate_selects(endpoints):
    for endpoint in endpoints.values():
        for select in endpoint.selects:
            if select.endpoint not in endpoints:
                raise ValueError(f'Select from not existing endpoint: {select.endpoint}')


def validate_pagination_key(endpoints):
    for endpoint in endpoints.values():
        if endpoint.pagination_enabled and endpoint.key is None:
            raise ValueError(f'Pagination enabled for endpoint withou key specified: {endpoint}')


class EndpointStorage:
    endpoints: Dict[str, Endpoint] = None


def load_endpoints():
    files = (
        os.path.join(settings.QUERIES_DIR, file)
        for file in os.listdir(settings.QUERIES_DIR)
    )
    files = [file for file in files if os.path.isfile(file) and file.endswith('.yaml')]
    endpoints = {}
    config = Config(forward_references={
        'Object': Object,
        'Select': Select,
        'Field': Field
    }, type_hooks={
        TypeEnum: TypeEnum.create
    })
    for file in files:
        with open(file) as f:
            data = yaml.safe_load(f)
            endpoint = from_dict(data_class=Endpoint, data=data, config=config)
            endpoints[endpoint.name] = endpoint

    validate_selects(endpoints)
    validate_pagination_key(endpoints)

    EndpointStorage.endpoints = endpoints

    return endpoints
