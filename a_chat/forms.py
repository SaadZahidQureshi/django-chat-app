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



    
