from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api.endpoint import Endpoint
from api.endpoint_loader import load_endpoints
from api.endpoint_processor import EndpointProcessor
from api.renderers import ApiXmlRenderer
from api.swagger import ApiSwaggerAutoSchema
from api.utils import http_headers


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

    @method_decorator(cache_page(settings.API_RESPONSE_CACHE_TIMEOUT_SECONDS))
    def get(self, request, *args, **kwargs):
        request_params = request.GET
        result = EndpointProcessor(self.endpoint).process(request_params, request)
        return Response(result)


def generate_endpoint_views():
    return {
        name: EndpointView.as_view(endpoint=ep)
        for name, ep in load_endpoints().items()
    }
