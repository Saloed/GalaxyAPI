import jsonfield

from django.db import models


class Query(models.Model):
    sql_file_name = models.CharField(unique=True, max_length=255)


class Endpoint(models.Model):
    name = models.CharField(unique=True, db_index=True, max_length=255)
    query = models.OneToOneField(Query, on_delete=models.CASCADE)
    pagination_key = models.CharField(max_length=255, null=True)


class EndpointParameter(models.Model):
    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE,
                                 related_name='parameters', related_query_name='parameter')
    name = models.CharField(max_length=255)
    condition = models.TextField(blank=True)
    required = models.BooleanField()
    sql_required = models.BooleanField()

    class Meta:
        unique_together = ['endpoint', 'name']


class EndpointSelect(models.Model):
    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE,
                                 related_name='endpoint_selects', related_query_name='endpoint_select')
    select_from = models.ForeignKey(Endpoint, on_delete=models.CASCADE,
                                    related_name='dependent', related_query_name='dependent')
    parameters = jsonfield.JSONField()


class SchemaDescription(models.Model):
    endpoint = models.OneToOneField(Endpoint, on_delete=models.CASCADE,
                                    related_name='schema', related_query_name='schema')
    # todo: add fields
