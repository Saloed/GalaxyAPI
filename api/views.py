import datetime
from collections import defaultdict
from typing import List, Dict, Any

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api import query_execution
from api.endpoint import Endpoint, SchemaFieldType, Field, Select, Object, Parameter, TypeEnum
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

    def validate_parameter(self, param, param_name: str, param_type: TypeEnum):
        if param_type in (TypeEnum.STRING, TypeEnum.INT, TypeEnum.BOOL):
            converters = {TypeEnum.STRING: str, TypeEnum.INT: int, TypeEnum.BOOL: bool}
            converter = converters[param_type]
            try:
                converter(param)
                return param
            except Exception:
                message = f"Incorrect parameter {param_name}: expected {param_type.value}, actual {param}"
                raise SuspiciousOperation(message)
        elif param_type in (TypeEnum.DATETIME, TypeEnum.DATE):
            formats = {TypeEnum.DATETIME: "%d.%m.%Y %H:%M:%S", TypeEnum.DATE: "%d.%m.%Y"}
            _format = formats[param_type]
            try:
                parsed = datetime.datetime.strptime(param, _format)
                if param_type == TypeEnum.DATE:
                    parsed = parsed.date()
                return parsed
            except Exception:
                message = f"Incorrect format for parameter {param_name}: expected {_format}, actual {param}"
                raise SuspiciousOperation(message)
        return param

    def process_parameters(self, request_params):
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

        sql_parameters = []
        sql_required_parameters = []
        for param in self.endpoint.params:
            if param.name not in request_params:
                continue
            value = request_params[param.name]
            validated_value = self.validate_parameter(value, param.name, param.type)
            sql_param = query_execution.Param(param.name, param.condition, validated_value)
            sql_parameters.append(sql_param)

        for param in sorted(self.endpoint.sql_params, key=lambda it: it.position):
            value = request_params[param.name]
            validated_value = self.validate_parameter(value, param.name, param.type)
            sql_param = query_execution.RequiredParam(param.name, validated_value)
            sql_required_parameters.append(sql_param)

        return sql_parameters, sql_required_parameters

    @method_decorator(cache_page(settings.API_RESPONSE_CACHE_TIMEOUT_SECONDS))
    def get(self, request, *args, **kwargs):
        request_params = request.GET

        sql_parameters, sql_required_parameters = self.process_parameters(request_params)
        query = query_execution.Query(self.endpoint.sql)

        page = None
        if self.endpoint.pagination_enabled:
            page_number = int(request_params.get(settings.PAGE_QUERY_PARAM, 0))
            page_size = int(request_params.get(settings.PAGE_SIZE_QUERY_PARAM, settings.DEFAULT_PAGE_SIZE))
            page = query_execution.Page(self.endpoint.key, page_size, page_number)

        sql_page = None if self.endpoint.aggregation_enabled else page
        query_result = query_execution.execute_query(query, sql_required_parameters, sql_parameters, sql_page)

        selected_data = EndpointSelectWrapper(self.endpoint.selects)
        selected_data.load(query_result, request)

        if self.endpoint.aggregation_enabled:
            data = self.convert_data_aggregated(query_result, selected_data)
            if self.endpoint.pagination_enabled:
                idx_from = page.number * page.size
                idx_to = (page.number + 1) * page.size
                data = data[idx_from:idx_to]
        else:
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

    def convert_single_record_aggregated(self, record, all_data, field: SchemaFieldType,
                                         selected_data: EndpointSelectWrapper):
        if isinstance(field, Field):
            return record[field.db_name]
        elif isinstance(field, Select):
            return selected_data.get_data(field.endpoint, record)
        elif isinstance(field, Object):
            if not field.aggregate and not field.many:
                return {
                    key: self.convert_single_record_aggregated(record, all_data, value, selected_data)
                    for key, value in field.fields.items()
                }
            if not field.aggregate and field.many:
                return [
                    {
                        key: self.convert_single_record_aggregated(record, all_data, value, selected_data)
                        for key, value in field.fields.items()
                    } for record in all_data
                ]
            if field.aggregate and field.many:
                data = defaultdict(list)
                for item in all_data:
                    key = item[field.aggregation_field]
                    data[key].append(item)
                aggregated_data = list(data.values())

                return [
                    {
                        key: self.convert_single_record_aggregated(records[0], records, value, selected_data)
                        for key, value in field.fields.items()
                    }
                    for records in aggregated_data
                ]
            raise ValueError(f"Aggregation on non many field: {field}")

        else:
            raise ValueError(f"Unknown schema field type: {field}")

    def convert_data_aggregated(self, data: List[Dict[str, Any]], selected_data: EndpointSelectWrapper):
        result_data = defaultdict(list)
        for item in data:
            key = item[self.endpoint.key]
            result_data[key].append(item)
        return [
            self.convert_single_record_aggregated(records[0], records, self.endpoint.schema, selected_data)
            for records in result_data.values()
        ]


def generate_endpoint_views():
    return {
        name: EndpointView.as_view(endpoint=ep)
        for name, ep in load_endpoints().items()
    }
