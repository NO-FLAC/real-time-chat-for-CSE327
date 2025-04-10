from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
import json
from asgiref.sync import async_to_sync
from .models import *

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)

        # print(self.scope['url_route']['kwargs']['chatroom_name'])
        # print(self.chatroom_name)
        # print(self.chatroom)
        # print(self.channel_layer)

        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )

        if self.user not in self.chatroom.users_online.all():
            print("pass")
            self.chatroom.users_online.add(self.user)
            self.update_online_count()

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )

        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']

        message = GroupMessage.objects.create(
            group=self.chatroom,
            author=self.user,
            body=body
        )

        event = {
            'type':'message_handler',
            'message_id': message.id
        }

        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

    def message_handler(self, event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)
        context = {
            'message': message,
            'user': self.user
        }

        html = render_to_string("partials/chat_message_p.html", context = context)
        self.send(text_data=html)

    def update_online_count(self):
        online_count = self.chatroom.users_online.count() - 1

        event = {
            'type': 'online_count_handler',
            'online_count': online_count
        }
        async_to_sync(self.channel_layer.group_send)(self.chatroom_name, event)

    def online_count_handler(self, event):
        online_count = event['online_count']
        print('online=============>',online_count)

        context = {
            'online_count' : online_count,
            'chat_group' : self.chatroom,
            # 'users': users
        }

        print(self.chatroom.users_online.all())

        html = render_to_string("partials/online_count.html", context=context)
        self.send(text_data=html)