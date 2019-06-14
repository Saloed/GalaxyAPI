import builtins
import inspect
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from api import description_parser
from api.models import *


class Command(BaseCommand):
    help = 'Load descriptions to database'

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

        entries, selects, params = [], [], []
        for desc in descriptions:
            endpoint_id = endpoint_ids[desc.name]
            selects += [
                EndpointSelect(
                    endpoint_id=endpoint_id,
                    select_from_id=endpoint_ids[select.endpoint_name],
                    parameters=select.required_params,
                    select_to_field_name=select.field_name
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

            schema = SchemaDescription.objects.create(endpoint_id=endpoint_id)

            entries += [
                SchemaEntry(
                    schema=schema,
                    entry_type=entry.entry_type,
                    name=entry.field_name,
                    value=entry.value,
                    type=entry.type,
                    level=entry.level
                )
                for entry in desc.fields_description
            ]

        EndpointParameter.objects.bulk_create(params)
        EndpointSelect.objects.bulk_create(selects)
        SchemaEntry.objects.bulk_create(entries)

    def handle(self, *args, **options):
        self.drop_everything()
        descriptions = self.load_descriptions()
        descriptions = self.parse_descriptions(descriptions)
        self.store_to_database(descriptions)
