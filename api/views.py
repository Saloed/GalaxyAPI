from typing import List, Dict, Any

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api import query_execution
from api.endpoint import Endpoint, SchemaFieldType, Field, Select, Object
from api.endpoint_data_wrapper import EndpointSelectWrapper
from api.endpoint_loader import load_endpoints
from api.renderers import ApiXmlRenderer
from api.swagger import ApiSwaggerAutoSchema
from api.utils import replace_query_param, http_headers


class ApiKeyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        api_key = settings.API_KEY
        if api_key is None:
            return False
        headers = http_headers(request)
        request_key = headers.get(settings.API_KEY_HEADER_NAME, None)
        if request_key is None:
            return False
        if request_key != api_key:
            return False
        return True


class EndpointView(APIView):
    renderer_classes = [JSONRenderer, ApiXmlRenderer]
    permission_classes = (ApiKeyPermission,)

    endpoint: Endpoint = None
    swagger_schema = ApiSwaggerAutoSchema

    def get(self, request, *args, **kwargs):
        request_params = request.GET

        required_parameters = self.endpoint.sql_params + [
            param
            for param in self.endpoint.params
            if param.required
        ]
        unspecified_parameters = [
            param for param in required_parameters
            if param.name not in request_params
        ]
        if unspecified_parameters:
            parameter_names = ', '.join([param.name for param in unspecified_parameters])
            raise SuspiciousOperation(f"Required parameters not specified: {parameter_names}")

        sql_parameters = [
            query_execution.Param(param.name, param.condition, request_params[param.name])
            for param in self.endpoint.params
            if param.name in request_params
        ]
        sql_required_parameters = self.endpoint.sql_params[:]
        sql_required_parameters.sort(key=lambda it: it.position)
        sql_required_parameters = [
            query_execution.RequiredParam(param.name, request_params[param.name])
            for param in sql_required_parameters
        ]
        query = query_execution.Query(self.endpoint.sql)

        if self.endpoint.aggregation_enabled:
            # todo: aggregation
            raise NotImplemented

            pass

        page = None
        if self.endpoint.pagination_enabled:
            page_number = int(request_params.get(settings.PAGE_QUERY_PARAM, 0))
            page_size = int(request_params.get(settings.PAGE_SIZE_QUERY_PARAM, settings.DEFAULT_PAGE_SIZE))
            page = query_execution.Page(self.endpoint.key, page_size, page_number)

        query_result = query_execution.execute_query(query, sql_required_parameters, sql_parameters, page)

        selected_data = EndpointSelectWrapper(self.endpoint.selects)
        selected_data.load(query_result, request)

        data = self.convert_data(query_result, selected_data)

        if self.endpoint.pagination_enabled:
            data_with_pagination = self.paginate(request, data, page)
            return Response(data_with_pagination)
        else:
            return Response(data)

    def paginate(self, request, data, page):
        url = request.build_absolute_uri()
        has_prev = page.number > 0
        has_next = len(data) == page.size
        prev_link, next_link = None, None
        if has_prev:
            prev_link = replace_query_param(url, settings.PAGE_QUERY_PARAM, page.number - 1)
        if has_next:
            next_link = replace_query_param(url, settings.PAGE_QUERY_PARAM, page.number + 1)

        return {
            'has_next': has_next,
            'has_prev': has_prev,
            'prev': prev_link,
            'next': next_link,
            'data': data
        }

    def convert_single_record(self, record, field: SchemaFieldType, selected_data: EndpointSelectWrapper):
        if isinstance(field, Field):
            return record[field.db_name]
        elif isinstance(field, Select):
            return selected_data.get_data(field.endpoint, record)
        elif isinstance(field, Object):
            return {
                key: self.convert_single_record(record, value, selected_data)
                for key, value in field.fields.items()
            }
        else:
            raise ValueError(f"Unknown schema field type: {field}")

    def convert_data(self, data: List[Dict[str, Any]], selected_data: EndpointSelectWrapper):
        return [
            self.convert_single_record(record, self.endpoint.schema, selected_data)
            for record in data
        ]


def generate_endpoint_views():
    return {
        name: EndpointView.as_view(endpoint=ep)
        for name, ep in load_endpoints().items()
    }
