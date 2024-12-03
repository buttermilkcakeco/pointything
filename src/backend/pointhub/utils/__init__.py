""" API utils """

import datetime
from pytz import utc
import random
import string

def stamp(dt=None):
    """ Convert a datetime into a millisecond timestamp """
    return int(dt.timestamp() * 1000) if dt else ''

def destamp(t):
    """ Convert a millisecond timestamp into a datetime """
    dt = datetime.datetime.fromtimestamp(t / 1000.0, tz=utc)
    return dt.replace(microsecond=((t % 1000) * 1000))

def create_id():
    """ Create a random ID """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
