from django.forms import ModelForm
from django import forms
from .models import *


class ChatMessageCreateForm(forms.ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['body']
        widgets = {
            'body' :forms.TextInput(attrs={
                "placehoder": "Add message ...",
                "class": "p-4 text-black",
                "max_length": 300,
                "auto_focus": True
            })
        }


class NewGroupForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ["groupchat_name"]
        widget = {
            "groupchat_name": {
                forms.TextInput(attrs={
                    "placeholder": "Add Name...",
                    "class": "p-4 text-black",
                    "maxlength": 300,
                    "autofocus": True
                })
            }
        }

class ChatRoomEditForm(forms.ModelForm):
    
    class Meta:
        model = ChatGroup
        fields = ['groupchat_name']
        widget = {
            'groupchat_name':{
                forms.TextInput(attrs={
                    "class": "p-4 text-xl font-bold mb-4",
                    "maxlength": 300                    
                })
            }
        }

    
