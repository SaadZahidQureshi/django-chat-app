from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
from . models import *
import json

class ChatroomConsumer(WebsocketConsumer):

    def connect(self):
        self.user = self.scope['user']
        self.chatroom_id = self.scope['url_route']['kwargs']["chatroom_name"]
        self.chatroom = get_object_or_404(ChatGroup, id=self.chatroom_id)
        
        # Accept the WebSocket connection
        self.accept()

        # Add the user to the chatroom group
        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_id, self.channel_name
        )

    def disconnect(self, code):
        # Remove the user from the chatroom group
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_id, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']
        
        # Create a new message in the chatroom
        message = GroupMessage.objects.create(
            body=body,
            group=self.chatroom,
            author=self.user
        )

        # Prepare the event for sending the message
        event = {
            "type": "message_handler",
            "message_id": message.id 
        }

        # Send the message event to the chatroom group
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_id, event
        )

    def message_handler(self, event):
        message_id = event["message_id"]
        message = GroupMessage.objects.get(id=message_id)
        context = {
            'message': message,
            'user': self.user
        }
        
        # Render the message as HTML
        html = render_to_string("a_chat/partials/chat_message_p.html", context)
        
        # Send the rendered message to the WebSocket
        self.send(text_data=html)
