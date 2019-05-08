import builtins
import inspect
import os
from typing import List, Dict, Any

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View

from api import description_parser
from api import query_execution
from api.endpoint_data_wrapper import EndpointSelectWrapper
from api.models import *
from api.response import json_response, xml_response
from api.utils import replace_query_param


class DispatchView(View):
    http_method_names = ['get']

    def get(self, request, type, endpoint, *args, **kwargs):

        endpoint_query = Endpoint.objects.prefetch_related(
            'parameters', 'endpoint_selects', 'query', 'schema', 'endpoint_selects__select_from'
        )
        endpoint = get_object_or_404(endpoint_query, name=endpoint)

        parameters = list(endpoint.parameters.all())
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
        query = query_execution.Query(endpoint.query.sql_file_name)
        page = None
        if endpoint.pagination_key is not None:
            page_number = int(request_params.get(settings.PAGE_QUERY_PARAM, 0))
            page = query_execution.Page(endpoint.pagination_key, settings.PAGE_SIZE, page_number)

        query_result = query_execution.execute_query(query, sql_required_parameters, sql_parameters, page)

        selected_data = EndpointSelectWrapper(type, endpoint.endpoint_selects.all())
        selected_data.load(query_result, request)

        data = self.convert_data(query_result, selected_data, endpoint.schema)

        data_with_pagination = self.paginate(request, data, page)

        if type == 'json':
            return json_response(data_with_pagination)
        elif type == 'xml':
            return xml_response(data_with_pagination, endpoint)
        else:
            raise ValueError(f"Unknown response type: {type}")

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

    def convert_data(self, data: List[Dict[str, Any]],
                     selected_data: EndpointSelectWrapper, schema: SchemaDescription):

        # todo: implement convertation according to schema. For now, schema is empty and convertation is dummy

        # todo: normaly Select items are in schema.
        select_items = selected_data.endpoints_data_wrappers.keys()
        select_items = [description_parser.Select(it) for it in select_items]

        for row in data:
            for select_item in select_items:
                selection_name = f'selected_{select_item.endpoint_name}'
                row[selection_name] = selected_data.get_data(select_item, row)

        return data


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
                    select_from_id=endpoint_ids[select.endpoint_name.lower()],
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
