import json
import re
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from rest_framework.request import Request


class AddDataMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if re.search('api_admin/', request.path) and request.method in ['POST'] and not re.search('login/', request.path):
            if isinstance(request, HttpRequest):
                # If the request is a standard Django HttpRequest
                if hasattr(request, 'POST'):
                    request.POST = request.POST.copy()
                    request.POST['data'] = request.POST
                    # print(request.POST)
                # elif hasattr(request, 'PUT'):
                #     request.PUT = request.PUT.copy()
                #     request.PUT['data'] = request.PUT
                #     print(request.PUT)
                # elif hasattr(request, 'PATCH'):
                #     request.PATCH = request.PATCH.copy()
                #     request.PATCH['data'] = request.PATCH
                #     print(request.PATCH)
