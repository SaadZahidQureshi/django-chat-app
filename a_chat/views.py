from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *

# Create your views here.


def chat_view(request, chatroom_name= 'public-chat'):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_message.all()[:30]
    context ={
        "chat_messages": chat_messages,
        "chat_group": chat_group
    }
    
    form = ChatMessageCreateForm()
    
    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user =  member
                break
            
    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            if request.user.emailaddress_set.filter(verified=True).exists():
                chat_group.members.add(request.user)
            else:
                messages.warning(request, "You need to verify email to join the chat.")
                return redirect("profile-settings")
    
    if request.htmx:
        form = ChatMessageCreateForm(request.POST)
        
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context['message'] = message
            context['user'] = request.user
            return render(request, 'a_chat/partials/chat_message_p.html', context)
                
    context["form"] = form
    context["other_user"] = other_user
    context["chatroom_name"] = chatroom_name
    return render(request, 'a_chat/chat.html', context)

@login_required
def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect("home")
    
    other_user = User.objects.get(username=username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)
    
    if my_chatrooms.exists():
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
                chatroom = chatroom 
                break
            else:
                chatroom = ChatGroup.objects.create(is_private = True)
                chatroom.members.add(other_user, request.user)
    else:
        chatroom = ChatGroup.objects.create(is_private = True)
        chatroom.members.add(other_user, request.user)
        
    return redirect("chatroom", chatroom.group_name)
    
@login_required
def create_groupchat(request):
    context = {}
    form = NewGroupForm()
    context["form"] = form
    
    if request.method == 'POST':
        form = NewGroupForm(request.POST)
        if form.is_valid():
            new_group  = form.save(commit=False)
            new_group.admin = request.user
            new_group.save()
            new_group.members.add(request.user)
            return redirect("chatroom", new_group.group_name)
    
    return render(request, "a_chat/create_groupchat.html", context)


def chatroom_edit_view(request, chatroom_name):
    context = {}
    chatroom = ChatGroup.objects.get(group_name = chatroom_name)
    
    if request.user != chatroom.admin:
        raise Http404()
    
    form = ChatRoomEditForm(instance=chatroom)
    
    if request.method == "POST":
        form = ChatRoomEditForm(request.POST, instance=chatroom)
        if form.is_valid():
            form.save()
            
            remove_members = request.POST.getlist("remove_members")
            for member in remove_members:
                user_member = User.objects.get(id=member)
                chatroom.members.remove(user_member)

            return redirect("chatroom", chatroom_name)
    
    
    context['form'] = form
    context['chat_group'] = chatroom
        
    return render(request, 'a_chat/chatroom_edit.html', context)


def chatroom_delete_view(request, chatroom_name):
    context = {}
    chatroom = ChatGroup.objects.get(group_name = chatroom_name)
    
    if request.user != chatroom.admin:
        raise Http404()
    
    if request.method == "POST":
        chatroom.delete()
        messages.success(request, "Chat room Deleted!")
        return redirect("home")   
    
    context['chat_group'] = chatroom
    return render(request, "a_chat/chatroom_delete.html", context)

def leave_chatroom_view(request, chatroom_name):
    chatroom = ChatGroup.objects.get(group_name = chatroom_name)
    
    if request.user not in chatroom.members.all():
        raise Http404()
    
    if request.method == 'POST':
        chatroom.members.remove(request.user)
        messages.success(request, "You left chat.")
        return redirect("home")
    
    return redirect("chatroom", chatroom_name)
        