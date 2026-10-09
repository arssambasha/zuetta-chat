import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django_redis import get_redis_connection

from .models import Group, Messages

class ChatConsumer(AsyncWebsocketConsumer):

    #Websocket connection
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()
      
     
    #Just disconnects the Websocket
    async def disconnect(self, close_code):
        print(close_code)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    #When the messsage was recevied it sends the data to chat_message()
    async def receive(self, text_data):
        
        user = self.scope['user']

        if not await self.is_rate_limited(user):
            await self.send(text_data=json.dumps({'error': 'rate limit exceeded'}))
            return

        message = json.loads(text_data)['message']
        saved = await self.save_message(user, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'chat_message', **saved}
        )

    #it is used to send a message to the connected WebSocket client
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'timestamp': timestamp,
        }))

    @database_sync_to_async
    def save_message(self, user, content):
        z_group = Group.objects.get(z_id=self.room_name)
        msg = Messages.objects.create(z_group=z_group, user=user, content=content)
        return {
            'message': msg.content,
            'username': user.username,
            'timestamp': msg.timestamp.isoformat(),
        }

    @database_sync_to_async
    def is_rate_limited(self, user):
        redis_conn = get_redis_connection("default")
        key = f"ratelimit:ws:{user.id}"

        count = redis_conn.incr(key)
        if (count == 1):
            redis_conn.expire(key, 10)

        return count <= 20