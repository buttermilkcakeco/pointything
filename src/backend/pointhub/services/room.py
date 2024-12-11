
from pointhub.utils import create_id

from . import cache

ROOM_EXPIRATION_S = 60*60

def _add_participant(room, name):
    participant = {'id': create_id(), 'name': name}
    room['participants'].append(participant)
    return participant

def _get_room(c, room_id):
    obj = c.json().get(room_id, '$')
    return obj[0] if obj else None

def _save_room(c, room):
    c.json().set(room['id'], '$', room)
    c.expire(room['id'], time=ROOM_EXPIRATION_S)

def _is_owner(room, user_id):
    return room['participants'][0]['id'] == user_id

def create(owner_name):
    room = {
        'id': create_id(),
        'revealed': False,
        'participants': []
    }
    _add_participant(room, owner_name)

    with cache.connection() as c:
        _save_room(c, room)

    return room

def get(room_id):
    with cache.connection() as c:
        return _get_room(c, room_id)

def join(room_id, user_name):
    with cache.connection() as c:
        room = _get_room(c, room_id)
        if not room:
            return None

        user_id = _add_participant(room, user_name)['id']
        _save_room(c, room)
        return user_id

def vote(room_id, user_id, points):
    with cache.connection() as c:
        room = _get_room(c, room_id)
        if not room:
            return None

        user = next((u for u in room['participants'] if u['id'] == user_id), None)
        if not user:
            return None

        if points is None:
            user.pop('vote', None)
        else:
            user['vote'] = points
        _save_room(c, room)
        return room

def set_reveal(room_id, revealed):
    with cache.connection() as c:
        room = _get_room(c, room_id)
        if not room:
            return None

        room['revealed'] = revealed
        _save_room(c, room)
        return room

def reset_votes(room_id):
    with cache.connection() as c:
        room = _get_room(c, room_id)
        if not room:
            return None

        for user in room['participants']:
            user.pop('vote', None)
        room['revealed'] = False
        _save_room(c, room)
        return room

def remove_user(room_id, req_user_id, del_user_id):
    with cache.connection() as c:
        room = _get_room(c, room_id)
        if not room or not _is_owner(room, req_user_id) or req_user_id == del_user_id:
            return None

        room['participants'] = [p for p in room['participants'] if p['id'] != del_user_id]
        _save_room(c, room)
        return room
