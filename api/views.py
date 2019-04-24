from django.db import connections
from django.http import HttpResponse, JsonResponse
from django.views import View


class NotImplementedHttpResponse(HttpResponse):
    status_code = 501


class DispatchView(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        response_type = kwargs['type']
        endpoint = kwargs['endpoint']
        if endpoint == 'tables':
            with connections['galaxy_db'].cursor() as cursor:
                cursor.execute('SELECT Name FROM sys.Tables')
                tables = cursor.fetchall()
                return JsonResponse(tables, safe=False)
        elif endpoint == "ping":
            return JsonResponse({'status':"OK"})

        return NotImplementedHttpResponse(f'{request}')
