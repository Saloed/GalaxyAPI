import dicttoxml

from django.http import JsonResponse, HttpResponse

from api.models import Endpoint


class XmlResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        kwargs.setdefault('content_type', 'application/xml')
        super().__init__(content=data, **kwargs)


def json_response(data):
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


def _make_xml_item_selector(endpoint: Endpoint):
    def select_name(parent):
        if parent == 'data':
            return endpoint.name
        return parent

    return select_name


def xml_response(data, endpoint: Endpoint):
    # todo: fix name selection
    name_selector = _make_xml_item_selector(endpoint)
    xml_data = dicttoxml.dicttoxml(data, attr_type=False, item_func=name_selector)
    return XmlResponse(xml_data)
