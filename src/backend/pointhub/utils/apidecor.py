import json
import traceback

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.urls import path

from .errors import ApiError
from .validators import ValidationContext

class RouteList:
    urlpatterns = []

    def register(self, api_path):
        def _decorator(f):
            self.urlpatterns.append(path(api_path, f))
            return f
        return _decorator

def _validate_fields(fields, request):
    if request.content_type == 'application/json':
        try:
            values = json.loads(request.body or '{}')
        except (TypeError, ValueError):
            raise ApiError(ApiError.ERRCODE_REQUEST_FORMAT)

    else:
        values = request.POST if request.method == 'POST' else request.GET
        values = values.copy()
        if 'jv' in values:
            try:
                values.update(json.loads(values['jv']))
            except (TypeError, ValueError):
                raise ApiError(ApiError.ERRCODE_REQUEST_FORMAT)

    values.update(request.FILES)

    ctx = ValidationContext()
    ctx.request = request
    ctx.values = values

    for field_name, validator, required in fields:
        if field_name in values:
            if validator:
                try:
                    values[field_name] = validator(ctx, values[field_name])
                except:
                    traceback.print_exc()
                    raise ApiError(ApiError.ERRCODE_INVALID_FIELD, field_name)

        elif required:
            raise ApiError(ApiError.ERRCODE_MISSING_FIELD, field_name)

    return values

def field_validation(fields):
    def _wrapper(f):
        def _decorator(request, *args, **kwargs):
            try:
                values = _validate_fields(fields, request)
                resp = f(request, values, *args, **kwargs)
            except ApiError as e:
                resp = JsonResponse(e.serialize())
                resp.status_code = 400
            except PermissionDenied:
                resp = HttpResponse(status=403)

            return resp

        return _decorator
    return _wrapper

def json_response(f):
    def _decorator(*args, **kwargs):
        resp = f(*args, **kwargs)
        if not isinstance(resp, HttpResponse):
            resp = JsonResponse(resp)
        return resp
    return _decorator
