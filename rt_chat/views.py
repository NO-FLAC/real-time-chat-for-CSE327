from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib import messages
from .models import *
from .forms import *

# Create your views here.

@login_required
def chat_view(request, chatroom_name='public-chat'):
    print("chatroom=======>", chatroom_name)
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatmessageCreateForm()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        
        for member in chat_group.members.all():
            if member!= request.user:
                other_user = member
                break

    if chat_group.groupchat_name:
        print("pass2")
        if request.user not in chat_group.members.all():
            print("pass2")
            if request.user.emailaddress_set.filter(verified=True).exists():
                chat_group.members.add(request.user)
            else:
                messages.warning(request, 'You need to verify your email to join the chat!')
                return redirect('profile-settings')

    print('members=====>', chat_group.members.all())
    if request.htmx:
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()


            context = {
                'message': message,
                'user': request.user,
                'chat_group': chat_group,
                # 'chat_messages': chat_messages,
                # 'next': request.GET.get('next', '')
            }

            return render(request, 'partials/chat_message_p.html', context)
        
    context = {
                'chat_messages': chat_messages,
                'form': form,
                'other_user': other_user,
                'chatroom_name': chatroom_name,
                'chat_group' : chat_group
            }
    return render(request, 'chat.html', context = context)

@login_required
def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect('home')
    
    other_user = User.objects.get(username = username)
    my_private_chatrooms = request.user.chat_groups.filter(is_private=True)
    
    if my_private_chatrooms.exists():
        for chatroom in my_private_chatrooms:
            if other_user in chatroom.members.all():
                return redirect('chatroom', chatroom.group_name)
   
    chatroom = ChatGroup.objects.create( is_private = True )
    chatroom.members.add(other_user, request.user)   
    return redirect('chatroom', chatroom.group_name)

from abc import abstractmethod

class GroupCreator:
    @abstractmethod
    def factory_method(self, request):
        pass

    def createGroup(self, request):
        # Call the factory method to create a Product object.
        group = self.factory_method(request=request)

        return group
    
class PrivateGroupCreator(GroupCreator):
    def factory_method(self, request):
        form = NewGroupForm(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)

            print("created New Group===================")
            print(type(new_groupchat), '======================')
            print(new_groupchat, '=========================')

            return new_groupchat
    

@login_required
def create_groupchat(request):
    form = NewGroupForm()
    group_creator = PrivateGroupCreator()
    
    if request.method == 'POST':
        form = NewGroupForm(request.POST)
        new_groupchat = group_creator.createGroup(request=request)
        return redirect('chatroom', new_groupchat.group_name)
    
    context = {
        'form': form
    }
    return render(request, 'create_groupchat.html', context)

@login_required
def chatroom_edit_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    
    form = ChatRoomEditForm(instance=chat_group) 
    
    if request.method == 'POST':
        form = ChatRoomEditForm(request.POST, instance=chat_group)
        if form.is_valid():
            form.save()
            
            remove_members = request.POST.getlist('remove_members')
            for member_id in remove_members:
                member = User.objects.get(id=member_id)
                chat_group.members.remove(member)  
                
            return redirect('chatroom', chatroom_name) 
    
    context = {
        'form' : form,
        'chat_group' : chat_group
    }   
    return render(request, 'chatroom_edit.html', context)

@login_required
def chatroom_delete_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    
    if request.method == "POST":
        chat_group.delete()
        messages.success(request, 'Chatroom deleted')
        return redirect('home')
    
    return render(request, 'chatroom_delete.html', {'chat_group': chat_group})

@login_required
def chatroom_leave_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user not in chat_group.members.all():
        raise Http404()
    
    if request.method == "POST":
        chat_group.members.remove(request.user)
        messages.success(request, 'You left the Chat')
        return redirect('home')