# my_questions/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Post, Comment, Topic
from .forms import PostForm, CommentForm
from .views_user import *
from django.http import JsonResponse
from django.core.serializers import serialize

def post_list(request):
    Post.objects.all().delete()
    Topic.objects.all().delete()
    Topic.objects.create(id = 1, topic_name = "General Questions")
    Post.objects.create(id = 1, topic = Topic.objects.get(id=1), title = "Why is the sky blue?", body = "Hey guys, this might be a stupid question but why is the sky blue? Is there any specific reason?", score = -3)
    Comment.objects.create(id = 1, post = Post.objects.get(id=1), parent_comment = None, is_nested_comment = False, comment_number = 1, body = "This question is stupid", score = -1)
    Comment.objects.create(id = 2, post = Post.objects.get(id=1), parent_comment = Comment.objects.get(id=1), is_nested_comment = True, comment_number = 2, body = "Dont bully him thats not nice ", score = 5)
    Comment.objects.create(id = 3, post = Post.objects.get(id=1), parent_comment = Comment.objects.get(id=2), is_nested_comment = True, comment_number = 3, body = "shut up I can bully who I want ", score = -2)
    Comment.objects.create(id = 4, post = Post.objects.get(id=1), parent_comment = Comment.objects.get(id=1), is_nested_comment = True, comment_number = 4, body = "imagine if someone called u stupid how would u feel", score = 1)
 
    Topic.objects.create(id = 2, topic_name = "ECE651")
    Post.objects.create(id = 2, topic = Topic.objects.get(id=2), title = "Sample Post 1", body = "Sample Post", score = 2)
    Comment.objects.create(id = 5, post = Post.objects.get(id=2), parent_comment = None, is_nested_comment = False, comment_number = 1, body = "Sample Comment 1", score = 1)
    Comment.objects.create(id = 6, post = Post.objects.get(id=2), parent_comment = Comment.objects.get(id=5), is_nested_comment = True, comment_number = 2, body = "Sample Comment 2", score = 2)
   
    posts = Post.objects.all()
    return render(request, 'view_posts.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'view_post.html', {'post': post})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return HttpResponse(f"Post '{post.title}' created successfully!")
    else:
        form = CommentForm()
    return render(request, 'create_post.html', {'form': form})
