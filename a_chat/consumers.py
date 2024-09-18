from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
from . models import *
import json

class ChatroomConsumer(WebsocketConsumer):

    def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']["chatroom_name"]
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)
        
        # Accept the WebSocket connection
        self.accept()

        # Add the user to the chatroom group
        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name  # Changed from self.chatroom_id to self.chatroom_name
        )
        
        # Add and update online users
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()

            
            
    def disconnect(self, code):
        # Remove the user from the chatroom group
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )
        
        # remove and update online users
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()
        

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
            self.chatroom_name, event
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


    def update_online_count(self):
        online_count =self.chatroom.users_online.count() -1
        event = {
            'type': 'online_count_handler',
            'online_count': online_count
        }
        
        
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )
        
    def online_count_handler(self, event):
        online_count = event['online_count']
        context = {
            'online_count': online_count,
            "chat_group": self.chatroom
        }
        html = render_to_string('a_chat/partials/online_count.html', context)
        self.send(text_data=html)