from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .forms import *

# Create your views here.


def chat_view(request):
    public_chat = get_object_or_404(ChatGroup, id=1)
    messages = GroupMessage.objects.all()[:30]
    context ={
        "messages": messages,
    }
    
    form = ChatMessageCreateForm()
    
    if request.htmx:
        form = ChatMessageCreateForm(request.POST)
        
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = public_chat
            message.save()
            context['message'] = message
            context['user'] = request.user
            return render(request, 'a_chat/partials/chat_message_p.html', context)
                
    context["form"] = form
    return render(request, 'a_chat/chat.html', context)