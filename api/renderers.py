from rest_framework.exceptions import ErrorDetail
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

        xml = SimplerXMLGenerator(stream, self.charset, short_empty_elements=True)
        xml.startDocument()

        if self.is_error_response(data):
            self.render_error_response(xml, data)
        else:
            self.render_response(xml, data, endpoint)

        xml.endDocument()
        return stream.getvalue()

    def is_error_response(self, data):
        return 'detail' in data and isinstance(data['detail'], ErrorDetail)

    def render_error_response(self, xml, data):
        xml.startElement(self.root_tag_name, {})
        xml.startElement('error', {})
        xml.characters(force_text(data['detail']))
        xml.endElement('error')
        xml.endElement(self.root_tag_name)

    def render_response(self, xml, data, endpoint):
        if endpoint.pagination_enabled:
            pagination_attributes = {key: force_text(data.get(key)) for key in ['has_next', 'has_prev', 'prev', 'next']}
            content = data.get(endpoint.name, [])
            xml.startElement(endpoint.name, pagination_attributes)
            self.xml_for_endpoint(xml, content, endpoint)
            xml.endElement(endpoint.name)
        else:
            xml.startElement(endpoint.name, {})
            self.xml_for_endpoint(xml, data, endpoint)
            xml.endElement(endpoint.name)

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
            if not field.many:
                self.xml_for_object_fields(xml, field, name, item)
            else:
                xml.startElement(parent_name, {})
                for element in item:
                    self.xml_for_object_fields(xml, field, name, element)
                xml.endElement(parent_name)
        else:
            raise ValueError(f"Unknown schema field type: {field}")

    def xml_for_object_fields(self, xml, obj: Object, obj_name, item):
        attributes = [key for key, value in obj.fields.items() if self.field_is_attribute(value)]
        elements = [(key, value) for key, value in obj.fields.items() if not self.field_is_attribute(value)]
        serialized_attributes = {key: force_text(item[key]) for key in attributes}
        if not elements:
            xml.addQuickElement(obj_name, attrs=serialized_attributes)
            return
        xml.startElement(obj_name, serialized_attributes)
        for key, value in elements:
            self.xml_for_field(xml, item[key], key, value)
        xml.endElement(obj_name)

    def field_is_attribute(self, field):
        return isinstance(field, Field) and field.xml_attribute
