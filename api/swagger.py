from django.conf import settings
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from rest_framework.settings import api_settings

from api.endpoint import *
from api.endpoint_loader import EndpointStorage


class ApiSwaggerAutoSchema(SwaggerAutoSchema):
    pagination_parameters = [
        openapi.Parameter(
            name=settings.PAGE_QUERY_PARAM,
            description='Pagination page number',
            required=False,
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            default=0
        ),
        openapi.Parameter(
            name=settings.PAGE_SIZE_QUERY_PARAM,
            description='Pagination page size',
            required=False,
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            default=settings.DEFAULT_PAGE_SIZE
        ),
    ]

    format_parameters = [
        openapi.Parameter(
            api_settings.URL_FORMAT_OVERRIDE,
            description='Response format',
            required=False,
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            enum=['json', 'xml']
        )
    ]

    def __init__(self, view, path, method, components, request, overrides):
        super(SwaggerAutoSchema, self).__init__(view, path, method, components, request, overrides)
        endpoint: Endpoint = view.endpoint
        parameter_fields = self.endpoint_parameters(endpoint)
        normal_response = self.endpoint_response(endpoint)

        self.overrides['operation_summary'] = f'Get list of {endpoint.name}'
        self.overrides['operation_description'] = f'{endpoint.name} endpoint'
        self.overrides['manual_parameters'] = parameter_fields
        self.overrides['responses'] = {
            200: normal_response
        }

    def endpoint_parameters(self, endpoint: Endpoint):
        parameters = endpoint.parameters.all()
        parameter_fields = [
            openapi.Parameter(
                name=param.name,
                required=param.required,
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING
            )
            for param in parameters
        ]

        if endpoint.pagination_key is not None:
            parameter_fields += self.pagination_parameters

        parameter_fields += self.format_parameters
        return parameter_fields

    def endpoint_response(self, endpoint: Endpoint):
        endpoint_schema = self.endpoint_schema(endpoint)
        schema = openapi.Schema(properties={
            'has_next': openapi.Schema(description='next page is exist', type=openapi.TYPE_BOOLEAN),
            'has_prev': openapi.Schema(description='previous page is exist', type=openapi.TYPE_BOOLEAN),
            'next': openapi.Schema(description='next page link', type=openapi.TYPE_STRING),
            'prev': openapi.Schema(description='previous page link', type=openapi.TYPE_STRING),
            'data': openapi.Schema(description='response data', items=endpoint_schema, type=openapi.TYPE_ARRAY)
        }, type=openapi.TYPE_OBJECT)
        return openapi.Response('Normal', schema=schema)

    def endpoint_schema_field(self, field: SchemaFieldType):
        if isinstance(field, Field):
            return openapi.Schema(type=field.type.value, description=field.description)
        elif isinstance(field, Select):
            nested_endpoint = EndpointStorage.endpoints[field.endpoint]
            nested_endpoint_scheme = self.endpoint_schema(nested_endpoint)
            return openapi.Schema(
                description=f'{field.description}',
                items=nested_endpoint_scheme, type=openapi.TYPE_ARRAY
            )
        elif isinstance(field, Object):
            nested_result = {
                key: self.endpoint_schema_field(value)
                for key, value in field.fields.items()
            }
            return openapi.Schema(type=openapi.TYPE_OBJECT, properties=nested_result)
        else:
            raise ValueError(f"Unknown schema field type: {field}")

    def endpoint_schema(self, endpoint: Endpoint):
        result = self.endpoint_schema_field(endpoint.schema)
        result.title = endpoint.name
        return result
