from django.contrib import admin
from .models import *

# Register your models here.

class GroupMessageAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", )
    

    
admin.site.register(GroupMessage, GroupMessageAdmin)
admin.site.register(ChatGroup)
