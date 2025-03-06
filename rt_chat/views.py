from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *

# Create your views here.

@login_required
def chat_view(request):
    chat_group = get_object_or_404(ChatGroup, group_name='public-chat')
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatmessageCreateForm()

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
                # 'chat_group': chat_group,
                # 'chat_messages': chat_messages,
                # 'next': request.GET.get('next', '')
            }

            return render(request, 'partials/chat_message_p.html', context)
    return render(request, 'chat.html', {'chat_messages': chat_messages, 'form': form})