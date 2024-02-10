from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Post, Response
from .forms import *
from .views_user import *


def Home(request):
    posts = Post.objects.all().order_by("timestamp")
    context = {
        'posts': posts
    }
    return render(request, "base.html", context)


def post_detail(request, id):
    post = Post.objects.get(id=id)
    comment = CommentForm()
    reply = ReplyForm()

    if request.method == "POST":
        try:
            comment = CommentForm(request.POST)
            if comment.is_valid():  # check the form is valid
                c = comment.save(commit=False)  # commit = false delay the save
                c.user = request.user  # fetch the current user
                c.post = Post(id=id)  # fetch the current post
                c.save()  # then save
                redirect('/post/' + str(id) + '/' + str(c.id))  # parse the post_id and the comment_id

        except Exception as e:
            raise e

    context = {
        'post': post,
        'comment': comment,
        'reply': reply
    }
    return render(request, 'post_detail.html', context)


@login_required(login_url='register')
def create_post(request):
    form = PostForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        try:
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                # the commit = false check the post first, then commit to the database
                post.author = request.user
                post.save()
        except Exception as e:
            raise e

    return render(request, 'create_post.html', context)


@login_required(login_url='register')
def reply_list(request):
    if request.method == "POST":
        try:
            reply = ReplyForm(request.POST)
            if reply.is_valid():
                post_id = request.POST.get('post')
                parent_id = request.POST.get('parent')
                r = reply.save(commit=False)
                r.user = request.user
                r.post = Post(id=post_id)
                r.parent = Response(id=parent_id)
                r.save()
                redirect('/post/' + str(post_id) + '/' + str(r.id))

        except Exception as e:
            raise e

    return redirect('home')
