import traceback
from pprint import pprint

from rest_framework import status
from rest_framework.response import Response
from functools import wraps

from api.services.telegram import logging
from django.utils import translation


def api_decorator(func):
    def show_error_to_client(msg='Undefined error', code=status.HTTP_400_BAD_REQUEST):
        pprint(msg)

        response_data = {
            "status_code": code,
            "message": msg,
            "data": {}
        }

        return Response(response_data, status=code)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            data, msg, code = func(*args, **kwargs)

            if msg == "The user does not exist, OTP was sent successful":
                response = {
                    'status_code': 204,
                    'message': msg,
                    'data': data
                }
            else:
                response = {
                    'status_code': code,
                    'message': msg,
                    'data': data
                }
            print(response)
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            try:
                msg = str(e)
                stack_trace = traceback.format_exc()  # Lấy stack trace
                msg += f'\nStack Trace:\n{stack_trace}'

                try:
                    msg += f'| {str(args[1].build_absolute_uri())}'
                    msg += f'| {str(args[1].data)}'
                    msg += f'| {str(args[2])}' if len(args) >= 2 else ''
                except:
                    ...
                logging(msg=msg, active=True)
                if len(e.args) > 0:
                    error_value = e.args[0]

                    if isinstance(error_value, dict):
                        first_key = next(iter(error_value))
                        error_message = error_value[first_key]

                        if isinstance(error_message, list):
                            error_message = error_message[0]

                    else:
                        error_message = error_value
                else:
                    error_message = str(e)
                return show_error_to_client(msg=error_message.capitalize())

            except:
                return show_error_to_client(msg=str(e))

    return wrapper


def set_empty_string_if_none(func):
    @wraps(func)
    def wrapper(self, instance):
        data = func(self, instance)

        num_field = ['age']

        for field in data:
            if data[field] is None:
                data[field] = 0 if field in num_field else ''

        return data

    return wrapper


def activate_language(request):
    if 'HTTP_ACCEPT_LANGUAGE' in request.META:
        lang = request.META['HTTP_ACCEPT_LANGUAGE']
        translation.activate(lang)