from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'api/ws/roomhub/(?P<room_id>\w+)/(?P<user_id>\w+)$', consumers.ChatConsumer.as_asgi()),
]
