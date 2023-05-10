import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Message, Room
from django.contrib.auth.models import User
from textblob import TextBlob
import re
from better_profanity import profanity
from .bad_words import bad_words

# Load the bad words into the profanity filter
profanity.load_censor_words(bad_words)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"WebSocket connected for room {self.room_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        room = data['room']

        filtered_message = await self.filter_bad_words(message)

        await self.save_message(username, room, filtered_message)
        await self.channel_layer.group_send(
            self.room_group_name,{
                'type': 'chat_message',
                'message': filtered_message,
                'username': username,
                'room': room,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        room = event['room']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'room': room,
        }))

    @sync_to_async
    def save_message(self, username, room, message):
        user = User.objects.get(username=username)
        room = Room.objects.get(slug=room)
        Message.objects.create(user=user, room=room, content=message)

    async def filter_bad_words(self, message):
        sentiment = TextBlob(message).sentiment.polarity
        contains_profanity = profanity.contains_profanity(message)

        if sentiment < 0 or contains_profanity:
            message = '*' * len(message)
        return message
