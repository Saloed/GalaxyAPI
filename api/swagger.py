from django.conf import settings
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from rest_framework.settings import api_settings

from api.models import SchemaEntry


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
        endpoint = view.endpoint
        parameter_fields = self.endpoint_parameters(endpoint)
        normal_response = self.endpoint_response(endpoint)

        self.overrides['operation_summary'] = f'Get list of {endpoint.name}'
        self.overrides['operation_description'] = f'{endpoint.name} endpoint'
        self.overrides['manual_parameters'] = parameter_fields
        self.overrides['responses'] = {
            200: normal_response
        }

    def endpoint_parameters(self, endpoint):
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

    def endpoint_response(self, endpoint):
        endpoint_schema = self.endpoint_schema(endpoint)
        schema = openapi.Schema(properties={
            'has_next': openapi.Schema(description='next page is exist', type=openapi.TYPE_BOOLEAN),
            'has_prev': openapi.Schema(description='previous page is exist', type=openapi.TYPE_BOOLEAN),
            'next': openapi.Schema(description='next page link', type=openapi.TYPE_STRING),
            'prev': openapi.Schema(description='previous page link', type=openapi.TYPE_STRING),
            'data': openapi.Schema(description='response data', items=endpoint_schema, type=openapi.TYPE_ARRAY)
        }, type=openapi.TYPE_OBJECT)
        return openapi.Response('Normal', schema=schema)

    def endpoint_schema(self, endpoint):
        schema = list(endpoint.schema.entries.all())

        def build_data_by_schema(i, lvl, scheme):
            res = {}
            while i < len(scheme) and scheme[i].level == lvl:
                level_scheme: SchemaEntry = scheme[i]
                name = level_scheme.name
                if level_scheme.type == 'dict':
                    nested_result, i = build_data_by_schema(i + 1, level_scheme.level + 1, scheme)
                    res[name] = openapi.Schema(type=openapi.TYPE_OBJECT, properties=nested_result)
                    continue
                elif level_scheme.type == 'Select':
                    endpoint_name = level_scheme.value
                    field_name = level_scheme.name
                    nested_endpoint = endpoint.endpoint_selects.get(select_from__name=endpoint_name).select_from
                    nested_endpoint_scheme = self.endpoint_schema(nested_endpoint)
                    res[field_name] = openapi.Schema(
                        description=f'{nested_endpoint.name} data',
                        items=nested_endpoint_scheme, type=openapi.TYPE_ARRAY
                    )
                else:
                    _type = {
                        'str': openapi.TYPE_STRING,
                        'int': openapi.TYPE_INTEGER
                    }.get(level_scheme.type, level_scheme.type)
                    res[name] = openapi.Schema(type=_type)

                i += 1
            return res, i

        result, _ = build_data_by_schema(0, 0, schema)

        return openapi.Schema(title=endpoint.name, type=openapi.TYPE_OBJECT, properties=result)
