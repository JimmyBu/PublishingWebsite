import json
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Friend, Profile, ChatMessage
from .forms import ChatMessageForm, ProfileForm
from django.db import IntegrityError


def index(request):
    user = request.user.profile
    friends = user.friends.all()
    context = {
        "user": user,
        "friends": friends,
    }
    return render(request, 'mychatapp/index.html', context)


def detail(request, pk):
    friend = Friend.objects.get(profile_id=pk)
    user = request.user.profile
    profile = Profile.objects.get(id=friend.profile.id)
    form = ChatMessageForm()
    chats = ChatMessage.objects.all()
    rec_chats = ChatMessage.objects.filter(msg_sender=profile, msg_receiver=user)
    rec_chats.update(seen=True)
    if request.method == "POST":
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.msg_sender = user
            chat_message.msg_receiver = profile
            chat_message.save()
            return redirect("detail", pk=friend.profile.id)
    context = {
        "friend": friend,
        "form": form,
        "user": user,
        "profile": profile,
        "chats": chats,
        "num": rec_chats.count(),
    }
    return render(request, "mychatapp/detail.html", context)


def sentMessages(request, pk):
    user = request.user.profile
    friend = Friend.objects.get(profile_id=pk)
    profile = Profile.objects.get(id=friend.profile.id)
    data = json.loads(request.body)
    new_chat = data["msg"]
    new_chat_message = ChatMessage.objects.create(body=new_chat, msg_sender=user, msg_receiver=profile, seen=False)
    return JsonResponse(new_chat_message.body, safe=False)


def receivedMessages(request, pk):
    arr = []
    user = request.user.profile
    friend = Friend.objects.get(profile_id=pk)
    profile = Profile.objects.get(id=friend.profile.id)
    chats = ChatMessage.objects.filter(msg_sender=profile, msg_receiver=user)
    for chat in chats:
        arr.append(chat.body)
    return JsonResponse(arr, safe=False)


def chatNotification(request):
    arr = []
    user = request.user.profile
    friends = user.friends.all()
    for friend in friends:
        chats = ChatMessage.objects.filter(msg_sender__id=friend.profile.id, msg_receiver=user, seen=False)
        arr.append(chats.count())
    return JsonResponse(arr, safe=False)


@login_required
def create_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('index')
    else:
        form = ProfileForm()
    return render(request, 'mychatapp/create_profile.html', {'form': form})


@login_required
def add_friend(request, friend_id):
    friend_profile = get_object_or_404(Profile, id=friend_id)
    user_profile = request.user.profile

    # Check existence
    if user_profile.friends.filter(profile=friend_profile).exists():
        return redirect('friends_list')

    # Check Friend instance
    existing_friend = Friend.objects.filter(profile=friend_profile).first()

    if existing_friend:
        user_profile.friends.add(existing_friend)
        return redirect('friends_list')

    try:
        # Create new
        friend = Friend.objects.create(profile=friend_profile)
        user_profile.friends.add(friend)
    except IntegrityError:
        # Prevent Database overlapped
        return redirect('friends_list')

    return redirect('friends_list')


@login_required
def friends_list(request):
    user = request.user.profile
    friends = user.get_friends()
    return render(request, 'mychatapp/friends_list.html', {'friends': friends})


@login_required
def create_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            # Update the user's existing profile with the newly created one
            user_profile = UserProfile.objects.get_or_create(user=user)[0]
            user_profile.name = profile.name
            user_profile.pic = profile.pic
            user_profile.save()
            return redirect('index')
    else:
        form = ProfileForm()
    return render(request, 'mychatapp/create_profile.html', {'form': form})


def search_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = get_object_or_404(User, username=username)
        profile = user.profile
        return redirect('add_friend', friend_id=profile.id)
    else:
        pass
    return render(request, 'mychatapp/search_user.html')


