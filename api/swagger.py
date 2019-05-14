import coreapi
import coreschema
from rest_framework import exceptions
from rest_framework.permissions import AllowAny
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.request import clone_request
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator, ManualSchema
from rest_framework.schemas.generators import EndpointEnumerator
from rest_framework.views import APIView

from rest_framework_swagger import renderers

from api.models import Endpoint



class ViewStub:
    def __init__(self, schema):
        self.schema = ManualSchema(
            fields=[
                coreapi.Field(
                    "first_field",
                    required=True,
                    location="path",
                    schema=coreschema.String()
                ),
            ]
        )

    def check_permissions(self, request):
        return True


class ApiEndpointEnumerator(EndpointEnumerator):

    def get_api_endpoints(self, patterns=None, prefix=''):
        endpoints = Endpoint.objects.all()
        result = [
            (f'/api/json/{ep.name}', 'GET', None)
            for ep in endpoints
        ]
        return result


class ApiSchemaGenerator(SchemaGenerator):
    endpoint_inspector_cls = ApiEndpointEnumerator

    def create_view(self, callback, method, request=None):
        view = ViewStub(None)
        if request is not None:
            view.request = clone_request(request, method)
        return view


def get_swagger_view(title=None, url=None, patterns=None, urlconf=None):
    """
    Returns schema view which renders Swagger/OpenAPI.
    """

    class SwaggerSchemaView(APIView):
        _ignore_model_permissions = True
        exclude_from_schema = True
        permission_classes = [AllowAny]
        renderer_classes = [
            CoreJSONRenderer,
            renderers.OpenAPIRenderer,
            renderers.SwaggerUIRenderer
        ]

        def get(self, request):
            generator = ApiSchemaGenerator(
                title=title,
                url=url,
                patterns=patterns,
                urlconf=urlconf
            )
            schema = generator.get_schema(request=request)

            if not schema:
                raise exceptions.ValidationError(
                    'The schema generator did not return a schema Document'
                )

            return Response(schema)

    return SwaggerSchemaView.as_view()


schema_view = get_swagger_view(title='Api swagger schema')
