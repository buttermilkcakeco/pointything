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
            await self._bcast('roomUpdate', data)

    async def disconnect(self, close_code):
        logger.info('DISC %s %s', self.user_id, close_code)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        req = json.loads(text_data)

        logger.info('RX %s %s', self.user_id, req)

        if req['type'] == 'get':
            data = room.get(self.room_id)
            await self._send('roomUpdate', data)

        elif req['type'] == 'vote':
            points = req.get('data', None)
            data = room.vote(self.room_id, self.user_id, points)
            if data:
                await self._bcast('roomUpdate', data)

        elif req['type'] == 'unvote':
            data = room.vote(self.room_id, self.user_id, None)
            if data:
                await self._bcast('roomUpdate', data)

        elif req['type'] == 'reset':
            data = room.reset_votes(self.room_id)
            if data:
                await self._bcast('roomUpdate', data)

        elif req['type'] == 'reveal':
            data = room.set_reveal(self.room_id, True)
            if data:
                await self._bcast('roomUpdate', data)

        elif req['type'] == 'unreveal':
            data = room.set_reveal(self.room_id, False)
            if data:
                await self._bcast('roomUpdate', data)

    async def _send(self, msg_type, data):
        logger.info('SEND %s %s %s', self.user_id, msg_type, data)
        await self.send(text_data=json.dumps({'type': msg_type, 'data': data}))

    async def _bcast(self, msg_type, data):
        logger.info('BCAST %s %s %s', self.user_id, msg_type, data)
        await self.channel_layer.group_send(
            self.room_group_name, {'type': 'bcast.event', 'msg_type': msg_type, 'data': data}
        )

    async def bcast_event(self, event):
        msg_type = event['msg_type']
        data = event['data']
        await self._send(msg_type, data)
