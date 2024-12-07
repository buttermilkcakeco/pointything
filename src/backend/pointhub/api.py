from django.http import Http404

from .utils import validators
from .utils.apidecor import RouteList, field_validation, json_response
from .services import room

routes = RouteList()

@routes.register('createroom')
@field_validation((
    ('userName', validators.string(1, 32), True),
))
@json_response
def create_room(request, values):
    data = room.create(values['userName'])
    room_id = data['id']
    participant_id = data['participants'][0]['id']
    return {'redirect': f'/room/{room_id}/{participant_id}'}

@routes.register('room/<room_id>/join')
@field_validation((
    ('userName', validators.string(1, 32), True),
))
@json_response
def join_room(request, values, room_id):
    user_id = room.join(room_id, values['userName'])
    if not user_id:
        raise Http404('Unknown room')
    return {'user': user_id}
