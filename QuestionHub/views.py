# my_questions/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Post, Comment
from .forms import PostForm, CommentForm


def post_list(request):
    posts = Post.objects.all()
    return HttpResponse(f"Posts: {', '.join(post.title for post in posts)}")


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post)
    return HttpResponse(f"Post: {post.title}, Comments: {', '.join(comment.content for comment in comments)}")


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
