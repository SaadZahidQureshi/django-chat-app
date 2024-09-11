from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, unique=True)
    
    def __str__(self) -> str:
        return self.group_name
    

class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name="chat_message", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=300)
    created_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.author.username} :  {self.body}'
    
    class Meta:
        ordering = ['-id']
    