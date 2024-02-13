from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from django.contrib.auth import login, logout
from .models import Post, Response, Topic, UserProfile
from .forms import *
from django.contrib.auth import get_user_model

def Home(request):
    posts = Post.objects.all().order_by("timestamp")
    topics = Topic.objects.all()
    context = {
        'posts': posts,
        'topics' : topics,
        'current_page' : 'post'
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

def topic_detail(request, id):
    topic = Topic.objects.get(id=id)
    filtered_posts = Post.objects.all() if not topic else Post.objects.filter(topic_id=id)
    topics = Topic.objects.all()  # Assuming you need topics for the dropdown
    
    context = {
        'filtered_posts': filtered_posts,
        'topics': topics,
        'current_page' : 'topic_detail',
        'topic' : topic
    }
    return render(request, 'topic_detail.html', context)

def Register(request):
    form = RegisterUserForm()
    if request.method == "POST":
        try:
            form = RegisterUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                user_profile = UserProfile()
                user_profile.user = user
                user_profile.save()
                login(request, user)
                return redirect('home')
        except Exception as e:
            raise e  # Define the error

    context = {
        'form': form
    }
    return render(request, 'user.html', context)


# sketches
def Login(request):
    form = LoginForm

    if request.method == "POST":
        try:
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                # need to save the user data into the database.
                # I am not sure it is saved or not
                return redirect('home')
        except Exception as e:
            raise e

    context = {
        'form': form
    }
    return render(request, 'login.html', context)


@login_required(login_url='register')
def Logout(request):
    logout(request)
    return redirect('login')

@login_required
def my_profile(request):
    """
    view for user's own profile page
    :param request:html request
    :return:
    """
    current_user = request.user
    current_user_profile = UserProfile.objects.get(user=current_user)
    if not current_user.is_authenticated:
        return redirect("login")

    bio_form = EditBioForm(initial={'bio': current_user_profile.bio})
    if request.method == "POST":
        try:
            bio_form = EditBioForm(request.POST)
            if bio_form.is_valid():  # check the form is valid
                updated_profile = current_user_profile
                updated_bio = bio_form.save(commit=False)  # commit = false delay the save
                updated_profile.bio = updated_bio.bio
                updated_profile.save()  # then save
                return redirect("my_profile") #reload to show new bio
        except Exception as e:
            raise e

    return render(request, 'my_profile.html', context={'user': current_user, 'bio_form': bio_form})

def user_profile(request, id):
    """
    view for general user profile
    :param request:
    :param primary_key:
    :return:
    """
    User = get_user_model()

    if id == request.user.id:
        return redirect("my_profile")

    trgt_user = get_object_or_404(User, pk=id)
    return render(request, 'user_detail.html', context={'user': trgt_user})


@login_required(login_url='register')
def create_post(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # Redirect to the post detail page of the newly created post
            return redirect('post_detail', id=post.id)
    context = {'form': form}
    return render(request, 'create_post.html', context)

@login_required(login_url='register')
def create_topic(request):
    form = TopicForm()
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic_name = form.cleaned_data['name']
            # Check if a topic with the same name already exists
            existing_topic = Topic.objects.filter(name__iexact=topic_name).exists()
            if not existing_topic:
                topic = form.save()
                # Redirect to the topic detail page of the newly created topic
                return redirect('topic_detail', id=topic.id)
            else:
                form.add_error('name', 'A topic with this name already exists.')
    context = {'form': form}
    return render(request, 'create_topic.html', context)

@login_required(login_url='register')
def upvote_comment(request, pk, vote):
    comment = get_object_or_404(Response, pk=pk)
    if vote == 'U':
        comment.score += 1
    else:
        comment.score -= 1
    comment.save()

    original_url = request.META.get('HTTP_REFERER', '/default/url/')
    return redirect(original_url)

@login_required(login_url='register')
def upvote_post(request, pk, vote):
    post = get_object_or_404(Post, pk=pk)
    if vote == 'U':
        post.score += 1
    else:
        post.score -= 1
    post.save()

    original_url = request.META.get('HTTP_REFERER', '/default/url/')
    return redirect(original_url)

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
