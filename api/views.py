from typing import List, Dict, Any

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api import query_execution
from api.endpoint_data_wrapper import EndpointSelectWrapper
from api.models import *
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
        parameters = self.endpoint.parameters.all()
        request_params = request.GET

        unspecified_parameters = [
            param for param in parameters
            if param.required and param.name not in request_params
        ]
        if unspecified_parameters:
            parameter_names = ', '.join([param.name for param in unspecified_parameters])
            raise SuspiciousOperation(f"Required parameters not specified: {parameter_names}")

        sql_parameters = [
            query_execution.Param(param.name, param.condition, request_params[param.name])
            for param in parameters
            if not param.sql_required and param.name in request_params
        ]
        sql_required_parameters = [param for param in parameters if param.sql_required]
        sql_required_parameters.sort(key=lambda it: it.position)
        sql_required_parameters = [
            query_execution.RequiredParam(param.name, request_params[param.name])
            for param in sql_required_parameters
        ]
        query = query_execution.Query(self.endpoint.query.sql_file_name)
        page = None
        if self.endpoint.pagination_key is not None:
            page_number = int(request_params.get(settings.PAGE_QUERY_PARAM, 0))
            page_size = int(request_params.get(settings.PAGE_SIZE_QUERY_PARAM, settings.DEFAULT_PAGE_SIZE))
            page = query_execution.Page(self.endpoint.pagination_key, page_size, page_number)

        query_result = query_execution.execute_query(query, sql_required_parameters, sql_parameters, page)

        selected_data = EndpointSelectWrapper(self.endpoint.endpoint_selects.all())
        selected_data.load(query_result, request)

        data = self.convert_data(query_result, selected_data)

        data_with_pagination = self.paginate(request, data, page)

        return Response(data_with_pagination)

    def paginate(self, request, data, page):
        if page is None:
            return {
                'has_next': False,
                'has_prev': False,
                'prev': None,
                'next': None,
                'data': data
            }
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

    def convert_data(self, data: List[Dict[str, Any]], selected_data: EndpointSelectWrapper):

        scheme = list(self.endpoint.schema.entries.all())

        def build_data_by_schema(row, i, lvl):
            res = {}
            while i < len(scheme) and scheme[i].level == lvl:
                node_scheme = scheme[i]
                name = node_scheme.name
                if node_scheme.entry_type == SchemaEntry.NESTED:
                    res[name], i = build_data_by_schema(row, i + 1, node_scheme.level + 1)
                    continue
                elif node_scheme.entry_type == SchemaEntry.SELECT:
                    endpoint_name = node_scheme.value
                    field_name = node_scheme.name
                    res[field_name] = selected_data.get_data(endpoint_name, row)
                elif node_scheme.entry_type == SchemaEntry.DB:
                    value = node_scheme.value
                    res[name] = row[value]
                elif node_scheme.entry_type == SchemaEntry.NORMAL:
                    res[name] = row[name]
                i += 1
            return res, i

        result = [
            build_data_by_schema(row, 0, 0)[0]
            for row in data
        ]

        return result


def generate_endpoints():
    try:
        endpoints = Endpoint.objects.all().prefetch_related(
            'parameters', 'endpoint_selects', 'query', 'schema',
            'endpoint_selects__select_from', 'schema__entries'
        )
        return {
            ep.name: EndpointView.as_view(endpoint=ep)
            for ep in endpoints
        }
    except Exception as ex:
        return {}

