from django.http import HttpResponseForbidden, HttpResponseBadRequest
from sentry_sdk import capture_message


def catch_403_view(*args, **kwargs):
    capture_message('Unauthorized', level='warning')

    return HttpResponseForbidden('Forbidden')


def catch_400_view(*args, **kwargs):
    capture_message('Bad Request', level='warning')

    return HttpResponseBadRequest('Bad Request')
