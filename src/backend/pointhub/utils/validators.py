""" Common API field validators """

import json
import re

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import validate_email, URLValidator

from . import destamp

class ValidationContext:
    """ Context object passed to validation functions """
    request = None
    values = None

def compose(validators):
    """ Create one validator from multiple validators """

    def _validator(ctx, value):
        for validator in validators:
            value = validator(ctx, value)
        return value

    return _validator

def optional(validator):
    """ Create a validator that allows None """

    def _validator(ctx, value):
        return validator(ctx, value) if value else None

    return _validator

def any(ctx, value):
    """ A validate that accepts anything """
    return value

def string(min_length=0, max_length=None):
    """ Create a validator for a string """

    def _validator(ctx, value):
        value = str(value)
        if len(value) < min_length or (max_length and len(value) > max_length):
            raise ValueError
        return value

    return _validator

def boolean(ctx, value):
    """ A validator for a bool """

    if isinstance(value, str):
        value = value.lower() == 'true'
    else:
        value = bool(value)

    return value

def nullboolean(ctx, value):
    """ A validator for a bool that could be None """

    if isinstance(value, str):
        if not value:
            value = None
        else:
            value = value.lower() == 'true'
    else:
        value = bool(value)

    return value

def number(minval, maxval, coerce_type=int):
    """ Create a validator for an integer """

    def _validator(ctx, value):
        value = coerce_type(value)
        if value < minval or value > maxval:
            raise ValueError
        return value

    return _validator

def choices(options, type_coerce=int):
    """ Create a validator for a set of choices """

    def _validator(ctx, value):
        if type_coerce:
            value = type_coerce(value)

        if value not in options:
            raise ValueError

        return value

    return _validator

def json_object(ctx, value):
    """ Validate an object """
    if isinstance(value, str):
        value = json.loads(value)

    if not isinstance(value, dict):
        raise ValueError

    return value

def structured_object(fields):
    """ Validator for object with known structure """

    def _validator(ctx, value):
        value = json_object(ctx, value)

        obj = {}
        for name, validator, required in fields:
            if required and name not in value:
                raise ValueError
            if name in value:
                obj[name] = validator(ctx, value[name])

        return obj

    return _validator

def structured_list(elem_validator):
    """ Validator for a list of elements of known type """

    def _validator(ctx, value):
        if not isinstance(value, list):
            raise ValueError

        return [elem_validator(ctx, v) for v in value]

    return _validator

def stamp(ctx, value):
    """ Validate a timestamp and convert to datetime """
    value = int(float(value))
    if value < 0 or value > 2000000000000:
        raise ValueError
    value = destamp(value)

    return value

def regex(pattern):
    r = re.compile(pattern)

    """ Validate a string with a regex """
    def _validator(ctx, value):
        value = str(value)
        if value and not r.match(value):
            raise ValueError
        return value

    return _validator

def email(ctx, value):
    """ Validate an email address """
    value = str(value)
    if value:
        validate_email(value)
    return value

phone_number = regex(r'^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$')
ip_address = regex(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

_url_validator = URLValidator()
def url(ctx, value):
    """ Validate a URL """
    value = str(value)
    _url_validator(value)
    return value

def object_id(ctx, value):
    """ Validate an object ID """

    if isinstance(value, str):
        value = value.strip()
    value = int(value)
    if value < 1:
        raise ValueError

    return value

def db_object(base_qs):
    """ Validate a database object """

    def _validator(ctx, value):
        value = object_id(ctx, value)
        try:
            value = base_qs(ctx).get(id=value)
        except ObjectDoesNotExist:
            raise ValueError
        return value

    return _validator

def object_ids(ctx, value):
    """ Validate a list of object IDs """

    if isinstance(value, (int, str)):
        value = [object_id(ctx, value)]

    elif isinstance(value, list):
        value = [object_id(ctx, v) for v in value]

    else:
        raise ValueError

    return value

def db_objects(base_qs):
    """ Validate a database object queryset """

    def _validator(ctx, value):
        return base_qs(ctx).filter(id__in=object_ids(ctx, value))

    return _validator

def filefield(ctx, value):
    """ Validate a file """

    if not isinstance(value, UploadedFile):
        raise ValueError

    return value
