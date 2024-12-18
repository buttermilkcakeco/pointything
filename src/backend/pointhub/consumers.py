import copy
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from .services import room

_GROUP_NAME = 'chat'

logger = logging.getLogger('uvicorn.info')

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'room_{self.room_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        data = room.get(self.room_id)
        if data:
            await self._bcast(data)

    async def disconnect(self, close_code):
        logger.info('DISC %s %s', self.user_id, close_code)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        req = json.loads(text_data)

        logger.info('RX %s %s', self.user_id, req)

        data = None

        if req['type'] == 'vote':
            points = req.get('data', None)
            data = room.vote(self.room_id, self.user_id, points)

        elif req['type'] == 'unvote':
            data = room.vote(self.room_id, self.user_id, None)

        elif req['type'] == 'reset':
            data = room.reset_votes(self.room_id)

        elif req['type'] == 'reveal':
            data = room.set_reveal(self.room_id, True)

        elif req['type'] == 'unreveal':
            data = room.set_reveal(self.room_id, False)

        elif req['type'] == 'removeUser':
            user_id = req.get('data', None)
            data = room.remove_user(self.room_id, self.user_id, user_id)

        if req.get('seq'):
            await self._send('ack', req['seq'])

        if data:
            await self._bcast(data)

    async def _send(self, msg_type, data):
        logger.info('SEND %s %s %s', self.user_id, msg_type, data)
        await self.send(text_data=json.dumps({'type': msg_type, 'data': data}))

    async def _bcast(self, data):
        logger.info('BCAST %s %s', self.user_id, data)
        await self.channel_layer.group_send(
            self.room_group_name, {'type': 'bcast.room_update', 'data': data}
        )

    async def bcast_room_update(self, event):
        data = event['data']
        await self._send('roomUpdate', self._room_data(data))

    def _room_data(self, data):
        data = copy.deepcopy(data)
        data['isOwner'] = data['participants'][0]['id'] == self.user_id
        if not data['isOwner']:
            for p in data['participants']:
                if p['id'] != self.user_id:
                    del p['id']
        return data
