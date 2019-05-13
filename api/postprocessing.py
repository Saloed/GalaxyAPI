from typing import List, Dict, Any

from api import description_parser
from api.endpoint_data_wrapper import EndpointSelectWrapper
from api.models import Endpoint, SchemaDescription
from api.utils import BuilderTypeSelector, XMLNamedNode


class _ConvertationResultBuilder(BuilderTypeSelector):
    def build_json(self, data, *args, **kwargs):
        return data

    def build_xml(self, data, endpoint: Endpoint):
        return XMLNamedNode(data, endpoint.name)


def convert_data(type, data: List[Dict[str, Any]], selected_data: EndpointSelectWrapper, endpoint: Endpoint):
    schema: SchemaDescription = endpoint.schema
    # todo: implement convertation according to schema. For now, schema is empty and convertation is dummy

    # todo: normaly Select items are in schema.
    select_items = selected_data.endpoints_data_wrappers.keys()
    select_items = [description_parser.Select(it) for it in select_items]

    for row in data:
        for select_item in select_items:
            selection_name = f'selected_{select_item.endpoint_name}'
            row[selection_name] = selected_data.get_data(select_item, row)

    return _ConvertationResultBuilder(type).build(data, endpoint)
