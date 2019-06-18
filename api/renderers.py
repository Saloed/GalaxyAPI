from rest_framework_xml.renderers import XMLRenderer
from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.encoding import force_text

from six import StringIO

from api.endpoint import Endpoint, SchemaFieldType, Field, Select, Object
from api.endpoint_loader import EndpointStorage


class ApiXmlRenderer(XMLRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ''

        endpoint: Endpoint = renderer_context['view'].endpoint

        stream = StringIO()

        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        xml.startElement(self.root_tag_name, {})

        if endpoint.pagination_enabled:
            for key, value in data.items():
                xml.startElement(key, {})
                if key != 'data':
                    xml.characters(force_text(value))
                else:
                    self.xml_for_endpoint(xml, value, endpoint)
                xml.endElement(key)
        else:
            self.xml_for_endpoint(xml, data, endpoint)

        xml.endElement(self.root_tag_name)
        xml.endDocument()
        return stream.getvalue()

    def _to_xml(self, xml, data):
        return NotImplemented

    def xml_for_endpoint(self, xml, data, endpoint: Endpoint):
        schema: SchemaFieldType = endpoint.schema
        if isinstance(data, list):
            for item in data:
                self.xml_for_field(xml, item, endpoint.name, schema)
        else:
            self.xml_for_field(xml, data, endpoint.name, schema)

    def xml_for_field(self, xml, item, parent_name, field: SchemaFieldType):
        if isinstance(field, Field):
            xml.startElement(parent_name, {})
            xml.characters(force_text(item))
            xml.endElement(parent_name)
        elif isinstance(field, Select):
            xml.startElement(parent_name, {})
            select_from = EndpointStorage.endpoints[field.endpoint]
            self.xml_for_endpoint(xml, item, select_from)
            xml.endElement(parent_name)
        elif isinstance(field, Object):
            name = field.name or parent_name or 'item'
            xml.startElement(name, {})
            for key, value in field.fields.items():
                self.xml_for_field(xml, item[key], key, value)
            xml.endElement(name)
        else:
            raise ValueError(f"Unknown schema field type: {field}")
