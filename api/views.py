import builtins
import inspect
import os

from typing import List, Dict, Any

import coreapi
import coreschema

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse, HttpResponse
from django.views import View
from rest_framework.schemas import ManualSchema
from rest_framework.views import APIView

from api import description_parser
from api import query_execution
from api.endpoint_data_wrapper import EndpointSelectWrapper
from api.models import *
from api.utils import replace_query_param


class EndpointView(APIView):
    endpoint: Endpoint = None

    def get(self, request, *args, **kwargs):
        type = 'json'
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
            page = query_execution.Page(self.endpoint.pagination_key, settings.PAGE_SIZE, page_number)

        query_result = query_execution.execute_query(query, sql_required_parameters, sql_parameters, page)

        selected_data = EndpointSelectWrapper(type, self.endpoint.endpoint_selects.all())
        selected_data.load(query_result, request)

        data = self.convert_data(type, query_result, selected_data, self.endpoint.schema)

        data_with_pagination = self.paginate(request, data, page)

        # todo: XML response
        return JsonResponse(data_with_pagination, json_dumps_params={'ensure_ascii': False})

    def paginate(self, request, data, page):

        # todo: XML pagination

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

    def convert_data(self, type, data: List[Dict[str, Any]],
                     selected_data: EndpointSelectWrapper, schema: SchemaDescription):

        if type != 'json':
            # todo: implement for XML
            return []

        # todo: implement convertation according to schema. For now, schema is empty and convertation is dummy

        # todo: normaly Select items are in schema.
        select_items = selected_data.endpoints_data_wrappers.keys()
        select_items = [description_parser.Select(it) for it in select_items]

        for row in data:
            for select_item in select_items:
                selection_name = f'selected_{select_item.endpoint_name}'
                row[selection_name] = selected_data.get_data(select_item, row)

        return data


def _generate_endpoint(endpoint: Endpoint):
    parameters = endpoint.parameters.all()
    endpoint_parameter_fields = [
        coreapi.Field(
            param.name,
            required=param.required,
            location="query",
            schema=coreschema.String()
        )
        for param in parameters
    ]
    pagination_parameters = []
    if endpoint.pagination_key is not None:
        pagination_parameters = [
            coreapi.Field(
                settings.PAGE_QUERY_PARAM,
                required=False,
                location="query",
                schema=coreschema.Integer(description='Pagination page number', default=0)
            )
        ]
    schema = ManualSchema(
        fields=endpoint_parameter_fields + pagination_parameters,
        description=f'{endpoint.name} endpoint',
        encoding='UTF-8'
    )
    return EndpointView.as_view(endpoint=endpoint, schema=schema)


def generate_endpoints():
    endpoints = Endpoint.objects.all().prefetch_related(
        'parameters', 'endpoint_selects', 'query', 'schema', 'endpoint_selects__select_from'
    )
    return {
        ep.name: _generate_endpoint(ep)
        for ep in endpoints
    }


class ManageLoadView(View):
    http_method_names = ['get']

    def drop_everything(self):
        Query.objects.all().delete()

    def load_descriptions(self):
        files = (
            os.path.join(settings.QUERIES_DIR, file)
            for file in os.listdir(settings.QUERIES_DIR)
        )
        files = [file for file in files if os.path.isfile(file)]
        description_lines = []
        for file in files:
            with open(file) as f:
                description_lines += f.readlines()

        description_text = ''.join(description_lines)
        context = {call.__name__: call for call in description_parser.DESCRIPTION_CALLS}
        context['__builtins__'] = builtins
        definitions = dict()
        exec(description_text, context, definitions)
        descriptions = [
            definition
            for definition in definitions.values()
            if inspect.isclass(definition)
        ]
        return descriptions

    def parse_descriptions(self, descriptions):
        description_parsers = [
            description_parser.DescriptionParser(description)
            for description in descriptions
        ]
        for parser in description_parsers:
            parser.parse()
        return description_parsers

    def store_to_database(self, descriptions):
        sql_files = [desc.sql for desc in descriptions]
        queries = [Query(sql_file_name=sql_file) for sql_file in sql_files]
        Query.objects.bulk_create(queries)
        queries = dict(Query.objects.values_list('sql_file_name', 'id'))

        endpoints = [
            Endpoint(name=desc.name, query_id=queries[desc.sql], pagination_key=desc.pagination_key)
            for desc in descriptions
        ]
        Endpoint.objects.bulk_create(endpoints)
        endpoint_ids = dict(Endpoint.objects.values_list('name', 'id'))

        schemas, selects, params = [], [], []
        for desc in descriptions:
            endpoint_id = endpoint_ids[desc.name]
            selects += [
                EndpointSelect(
                    endpoint_id=endpoint_id,
                    select_from_id=endpoint_ids[select.endpoint_name],
                    parameters=select.required_params
                )
                for select in desc.selects_description
            ]
            params += [
                EndpointParameter(
                    endpoint_id=endpoint_id,
                    name=param.name,
                    condition=param.condition,
                    required=param.required,
                    sql_required=False,
                    position=None
                )
                for param in desc.params_description
            ]
            params += [
                EndpointParameter(
                    endpoint_id=endpoint_id,
                    name=param.name,
                    condition='',
                    required=True,
                    sql_required=True,
                    position=i
                )
                for i, param in enumerate(desc.required_params_description)
            ]

            # todo: store field descriptions
            desc.fields_description
            schemas.append(SchemaDescription(endpoint_id=endpoint_id))

        EndpointParameter.objects.bulk_create(params)
        EndpointSelect.objects.bulk_create(selects)
        SchemaDescription.objects.bulk_create(schemas)

    def get(self, request, *args, **kwargs):
        self.drop_everything()
        descriptions = self.load_descriptions()
        descriptions = self.parse_descriptions(descriptions)
        self.store_to_database(descriptions)

        return HttpResponse('OK')
