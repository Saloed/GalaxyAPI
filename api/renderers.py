from rest_framework_xml.renderers import XMLRenderer
from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.encoding import force_text

from six import StringIO

from api.endpoint import Endpoint


class _XMLNamedNode:
    def __init__(self, node, name):
        self.node = node
        self.name = name


class _EndpointDependency:
    def __init__(self, filed_name, endpoint, children):
        self.endpoint = endpoint
        self.filed_name = filed_name
        self.children = children


def _get_endpoints_recursively(endpoint: Endpoint, name):
    children = endpoint.endpoint_selects.prefetch_related('select_from').all()
    children = [
        _get_endpoints_recursively(select.select_from, select.select_to_field_name)
        for select in children
    ]
    children = {it.filed_name: it for it in children}
    return _EndpointDependency(name, endpoint, children)


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
        return _XMLNamedNode(data, endpoint.endpoint.name)
    else:
        return root


class ApiXmlRenderer(XMLRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ''

        endpoint = renderer_context['view'].endpoint

        dependency = _get_endpoints_recursively(endpoint, 'data')
        dependency = {'data': dependency}
        data = _rebuild_xml_result(data, None, dependency)

        stream = StringIO()

        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        xml.startElement(self.root_tag_name, {})

        self._to_xml(xml, data)

        xml.endElement(self.root_tag_name)
        xml.endDocument()
        return stream.getvalue()

    def _to_xml(self, xml, data):
        if isinstance(data, _XMLNamedNode):
            lst = data.node
            for item in lst:
                xml.startElement(data.name, {})
                self._to_xml(xml, item)
                xml.endElement(data.name)
        elif isinstance(data, (list, tuple)):
            raise ValueError('Unexpected XML structure: list')
        elif isinstance(data, dict):
            for key, value in data.items():
                xml.startElement(key, {})
                self._to_xml(xml, value)
                xml.endElement(key)

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(force_text(data))
