import json
from django.contrib.auth.models import User
from django.contrib.auth import  get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatMessage
from .forms import ChatMessageForm
from django.db import IntegrityError


def index(request):
    user = request.user
    friends = user.userprofile.friends.all()
    context = {
        "user": user,
        "friends": friends,
    }
    return render(request, 'mychatapp/index.html', context)


def detail(request, pk):
    User = get_user_model()
    friend = User.objects.get(id=pk)
    user = request.user
    form = ChatMessageForm()
    chats = ChatMessage.objects.all()
    rec_chats = ChatMessage.objects.filter(msg_sender=friend, msg_receiver=user)
    rec_chats.update(seen=True)
    if request.method == "POST":
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.msg_sender = user
            chat_message.msg_receiver = friend
            chat_message.save()
            return redirect("detail", pk=friend.id)
    context = {
        "friend": friend,
        "form": form,
        "user": user,
        "chats": chats,
        "num": rec_chats.count(),
    }
    return render(request, "mychatapp/detail.html", context)


def sentMessages(request, pk):
    user = request.user
    friend = User.objects.get(id=pk)
    data = json.loads(request.body)
    new_chat = data["msg"]
    new_chat_message = ChatMessage.objects.create(body=new_chat, msg_sender=user, msg_receiver=friend, seen=False)
    return JsonResponse(new_chat_message.body, safe=False)


def receivedMessages(request, pk):
    arr = []
    user = request.user
    friend = User.objects.get(id=pk)
    chats = ChatMessage.objects.filter(msg_sender=friend, msg_receiver=user)
    for chat in chats:
        arr.append(chat.body)
    return JsonResponse(arr, safe=False)


def chatNotification(request):
    arr = []
    user = request.user.userprofile
    friends = user.friends.all()
    for friend in friends:
        chats = ChatMessage.objects.filter(msg_sender__id=friend.id, msg_receiver=user.user, seen=False)
        arr.append(chats.count())
    return JsonResponse(arr, safe=False)


@login_required
def friends_list(request):
    user = request.user
    friends = user.userprofile.get_friends()
    return render(request, 'mychatapp/friends_list.html', {'friends': friends})