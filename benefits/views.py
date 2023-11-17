from django.http import HttpResponseForbidden, HttpResponseBadRequest
from sentry_sdk import capture_message
from rest_framework.views import exception_handler


def catch_403_view(*args, **kwargs):
    capture_message('Unauthorized', level='warning')

    return HttpResponseForbidden('Forbidden')


def catch_400_view(*args, **kwargs):
    capture_message('Bad Request', level='warning')

    return HttpResponseBadRequest('Bad Request')


def drf_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    capture_message(
        response.reason_phrase,
        level='warning',
    )

    return response
