from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count
from django.db.models import Sum
from django.contrib.auth import login, logout
from .models import Post, Response, Topic, Vote, UserProfile
from .forms import *
from .views_chat import *
from django.contrib.auth import get_user_model
import openai

#Credentials for test user:
#admin
#Password123!

def Home(request):
    ordering = request.GET.get('ordering', '-timestamp')
    current_user = request.user
    # Handle different ordering criteria
    if ordering == 'num_views':
        posts = Post.objects.all().order_by('-num_views')
    elif ordering == 'most_upvoted':
        posts = Post.objects.all().order_by('-score')
    elif ordering == 'most_downvoted':
        posts = Post.objects.all().order_by('score')
    else:
        # Default ordering by timestamp
        posts = Post.objects.all().order_by('-timestamp')
    
    topics = Topic.objects.all()
    trending_topics = Topic.objects.annotate(total_views=Sum('post__num_views')).order_by('-total_views')[:10]
    users = User.objects.all()
    user_votes = []
    post_vote_list = []
    if request.user.is_authenticated:
        user_votes = Vote.objects.filter(user=request.user)
        
        for vote in user_votes:
          post_vote_list.append(vote.post)

        friends_list = request.user.userprofile.get_friends()
    else:
        friends_list = None
    

    context = {
        'current_ordering': ordering,
        'posts': posts,
        'topics': topics,
        'current_page': 'post',
        'trending_topics': trending_topics,
        'users': users,
        'all_posts': posts,
        'friends': friends_list,
        'is_authenticated': request.user.is_authenticated,
        'current_user': current_user
    }
    
    if user_votes:
        context['user_votes'] = user_votes
    if post_vote_list:
        context['post_vote_list'] = post_vote_list
 
    return render(request, "base.html", context)

def modify_comment(comment):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "You are a text moderator for a forum site. Your job is to identify if there is any profanity or vulgarity in a comment left by a user, and modify the comment to replace those bad words. Example: Comment='what is happening my brothers' Since no modification is needed, Result='what is happening my brothers'. Also just give the result, do not give the reasoning as to what you identified. Now please moderate this comment:",
            },
            {
                "role": "user",
                "content": comment,
            },
        ],
    )
    modified_comment = response.choices[0].message.content
    # print(response.choices[0].message.content)
    return modified_comment

def post_detail(request, id):
    post = Post.objects.get(id=id)
    posts = Post.objects.all().order_by("timestamp")
    current_user = request.user
    topics = Topic.objects.all()
    trending_topics = Topic.objects.annotate(total_views=Sum('post__num_views')).order_by('-total_views')[:10]
    users = User.objects.all()
    comment = CommentForm()
    reply = ReplyForm()
    user_vote = []
    comment_vote_list = []
    user_votes = []
    if request.user.is_authenticated:
        user_votes = Vote.objects.filter(user=request.user)
        user_vote = Vote.objects.filter(user=request.user, post=post).first()
        for vote in user_votes:
          comment_vote_list.append(vote.comment)
    
    if request.method == "POST":
        try:
            comment = CommentForm(request.POST)
            if comment.is_valid():  # check the form is valid
                c = comment.save(commit=False)  # commit = false delay the save
                c.user = request.user  # fetch the current user
                c.post = Post(id=id)  # fetch the current post
                modified_comment = modify_comment(c.body)  # Call the function to modify the comment
                c.body = modified_comment
                c.save()  # then save
                user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
                user_profile.num_comments += 1
                user_profile.save()
                redirect('/post/' + str(id) + '/' + str(c.id))  # parse the post_id and the comment_id

        except Exception as e:
            raise e

    context = {
        'post': post,
        'comment': comment,
        'reply': reply,
        'all_posts': posts,
        'topics': topics,
        'trending_topics': trending_topics,
        'users': users,
        'current_user': current_user
    }
    
    if user_vote:
        context['user_vote'] = user_vote
    if user_votes:
        context['user_votes'] = user_votes
    if comment_vote_list:
        context['comment_vote_list'] = comment_vote_list
    
    user_profile = UserProfile.objects.get_or_create(user=post.author)[0]
    post.num_views += 1
    post.save()
    user_profile.total_views += 1
    user_profile.save()
    
    return render(request, 'post_detail.html', context)

def topic_detail(request, id):
    topic = Topic.objects.get(id=id)
    trending_topics = Topic.objects.annotate(total_views=Sum('post__num_views')).order_by('-total_views')[:10]
    filtered_posts = Post.objects.all() if not topic else Post.objects.filter(topic_id=id)
    ordering = request.GET.get('ordering', '-timestamp')
    current_user = request.user
    # Handle different ordering criteria
    if ordering == 'num_views':
        filtered_posts = Post.objects.all().order_by('-num_views') if not topic else Post.objects.filter(topic_id=id).order_by('-num_views')
    elif ordering == 'most_upvoted':
        filtered_posts = Post.objects.all().order_by('-score') if not topic else Post.objects.filter(topic_id=id).order_by('-score')
    elif ordering == 'most_downvoted':
        filtered_posts = Post.objects.all().order_by('score') if not topic else Post.objects.filter(topic_id=id).order_by('score')
    else:
        # Default ordering by timestamp
        filtered_posts = Post.objects.all().order_by('-timestamp') if not topic else Post.objects.filter(topic_id=id).order_by('-timestamp')
    topics = Topic.objects.all()
    users = User.objects.all()
    user_votes = []
    post_vote_list = []
    if request.user.is_authenticated:
        user_votes = Vote.objects.filter(user=request.user)
        
        for vote in user_votes:
          post_vote_list.append(vote.post)
    
    
    context = {
        'current_ordering': ordering,
        'filtered_posts': filtered_posts,
        'topics': topics,
        'current_page' : 'topic_detail',
        'topic' : topic,
        'users' : users,
        'trending_topics': trending_topics,
        'all_posts' : filtered_posts,
        'current_user': current_user
    }
    
    if user_votes:
        context['user_votes'] = user_votes
    if post_vote_list:
        context['post_vote_list'] = post_vote_list
 
    return render(request, 'topic_detail.html', context)

def Register(request):
    posts = Post.objects.all().order_by("timestamp")
    topics = Topic.objects.all()
    current_user = request.user
    trending_topics = Topic.objects.annotate(total_views=Sum('post__num_views')).order_by('-total_views')[:10]
    users = User.objects.all()
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
        'all_posts': posts,
        'trending_topics': trending_topics,
        'topics': topics,
        'users': users,
        'form': form,
        'current_user': current_user
        
    }
    return render(request, 'user.html', context)


# sketches
def Login(request):
    current_user = request.user
    posts = Post.objects.all().order_by("timestamp")
    topics = Topic.objects.all()
    trending_topics = Topic.objects.annotate(total_views=Sum('post__num_views')).order_by('-total_views')[:10]
    users = User.objects.all()
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
        'all_posts': posts,
        'trending_topics': trending_topics,
        'topics': topics,
        'users': users,
        'form': form,
        'current_user': current_user
    }
    return render(request, 'login.html', context)


@login_required(login_url='register')
def Logout(request):
    logout(request)
    return redirect('login')

@login_required
def editProfilePic(request):
    """
    Edit a profile picture
    :param request:
    :return:
    """
    if request.method == "POST":
        try:
            pic_form = EditPicForm(request.POST, request.FILES)
            if pic_form.is_valid():  # check the form is valid
                current_user = request.user
                current_user_profile = UserProfile.objects.get(user=current_user)
                updated_profile = current_user_profile
                updated_pic = pic_form.save(commit=False)  # commit = false delay the save
                updated_profile.pic = updated_pic.pic
                updated_profile.save()  # then save
                return redirect("my_profile") #reload to show new pic
        except Exception as e:
            raise e
    return HttpResponse(status=200)

@login_required
def my_profile(request):
    """
    view for user's own profile page
    :param request:html request
    :return:
    """
    posts = Post.objects.all().order_by("timestamp")
    topics = Topic.objects.all()
    trending_topics = Topic.objects.annotate(total_views=Sum('post__num_views')).order_by('-total_views')[:10]
    users = User.objects.all()
    current_user = request.user
    current_user_profile = UserProfile.objects.get(user=current_user)
    friends = current_user_profile.get_friends()
    if not current_user.is_authenticated:
        return redirect("login")

    bio_form = EditBioForm(initial={'bio': current_user_profile.bio})
    pic_form = EditPicForm()
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
    
    context = {
        'all_posts': posts,
        'trending_topics': trending_topics,
        'topics': topics,
        'users': users,
        'user': current_user,
        'bio_form': bio_form,
        'pic_form': pic_form,
        'friends': friends,
        'current_user': current_user
    }

    return render(request, 'my_profile.html', context)

def user_profile(request, id):
    """
    view for general user profile
    :param request:
    :param primary_key:
    :return:
    """
    User = get_user_model()
    current_user = request.user
    posts = Post.objects.all().order_by("timestamp")
    topics = Topic.objects.all()
    trending_topics = Topic.objects.annotate(total_views=Sum('post__num_views')).order_by('-total_views')[:10]
    users = User.objects.all()
    if id == request.user.id:
        return redirect("my_profile")

    trgt_user = get_object_or_404(User, pk=id)

    if request.user.is_authenticated:
        is_friend = request.user.userprofile.friends.filter(id=trgt_user.id).exists()
        got_friend_request = request.user.userprofile.friend_requests.filter(id=trgt_user.id).exists()
        sent_friend_request = trgt_user.userprofile.friend_requests.filter(id=request.user.id).exists()
    else:
        is_friend = False
        got_friend_request = False
        sent_friend_request = False
    
    context = {
        'all_posts': posts,
        'trending_topics': trending_topics,
        'topics': topics,
        'users': users,
        'user': trgt_user,
        'is_friend': is_friend,
        'got_friend_request': got_friend_request,
        'sent_friend_request': sent_friend_request,
        'current_user': current_user,
	'not_authenticated': not request.user.is_authenticated
    }
            
    return render(request, 'user_detail.html', context)


@login_required(login_url='register')
def create_post(request):
    current_user = request.user
    posts = Post.objects.all().order_by("timestamp")
    topics = Topic.objects.all()
    trending_topics = Topic.objects.annotate(total_views=Sum('post__num_views')).order_by('-total_views')[:10]
    users = User.objects.all()
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
            user_profile.num_posts += 1
            user_profile.save()
            # Redirect to the post detail page of the newly created post
            return redirect('post_detail', id=post.id)
    context = {
        'all_posts': posts,
        'trending_topics': trending_topics,
        'topics': topics,
        'users': users,
        'form': form,
        'current_user': current_user
    }
    return render(request, 'create_post.html', context)

@login_required(login_url='register')
def create_topic(request):
    current_user = request.user
    posts = Post.objects.all().order_by("timestamp")
    topics = Topic.objects.all()
    trending_topics = Topic.objects.annotate(total_views=Sum('post__num_views')).order_by('-total_views')[:10]
    users = User.objects.all()
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
    context = {
        'all_posts': posts,
        'topics': topics,
        'users': users,
        'trending_topics': trending_topics,
        'form': form
    }
    return render(request, 'create_topic.html', context)

@login_required
def edit_comment(request, comment_id):
    
    original_url = request.META.get('HTTP_REFERER', '/default/url/')
    comment = get_object_or_404(Response, pk=comment_id)

    if request.method == "POST":
        comment_form = CommentForm(request.POST, instance=comment)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.save()
            return redirect(original_url)
    else:
        comment_form = CommentForm(instance=comment)
    return render(request, 'edit_comment.html', {'comment_form': comment_form})

@login_required(login_url='register')
def upvote_comment(request, pk, vote):
    comment = get_object_or_404(Response, pk=pk)
    user = request.user
    user_profile = UserProfile.objects.get_or_create(user=comment.user)[0]
    original_url = request.META.get('HTTP_REFERER', '/default/url/')
    
    if vote == 'U':
    # Check if the user has already upvoted this post, if they have undo upvote
        existing_vote = Vote.objects.filter(user=user, comment=comment).first()
        if existing_vote and existing_vote.vote_type == 'U':
            existing_vote.delete()
            comment.score -= 1
            user_profile.karma -= 1
            comment.save()
            user_profile.save()
            return redirect(original_url)
           
            #If there is an exisitng downvote, remove it, then add a new upvote
        elif existing_vote and existing_vote.vote_type == 'D':
            existing_vote.delete()
            comment.score += 2
            user_profile.karma += 2
            comment.save()
            user_profile.save()
            Vote.objects.create(user=user, comment=comment, vote_type='U')
            return redirect(original_url)
    # Otherwise create a new upvote
        else:
            Vote.objects.create(user=user, comment=comment, vote_type='U')
            comment.score += 1
            comment.save()
            user_profile.karma += 1
            user_profile.save()
            return redirect(original_url) 
    #Else vote is downvote
    else:
        existing_vote = Vote.objects.filter(user=user, comment=comment).first()
        #Check if there is an existing downvote, if so undo it
        if existing_vote and existing_vote.vote_type == 'D':
            existing_vote.delete()
            comment.score += 1
            user_profile.karma += 1
            comment.save()
            user_profile.save()
            return redirect(original_url) 
        
        #If there is an exisitng upvote, remove it, then add a downvote
        elif existing_vote and existing_vote.vote_type == 'U':
            existing_vote.delete()
            comment.score -= 2
            user_profile.karma -= 2
            comment.save()
            user_profile.save()
            Vote.objects.create(user=user, comment=comment, vote_type='D')
            return redirect(original_url)
        
        #Otherwise create a new downvote
        else:
            Vote.objects.create(user=user, comment=comment, vote_type='D')
            comment.score -= 1
            comment.save()
            user_profile.karma -= 1
            user_profile.save()
            return redirect(original_url) 

@login_required(login_url='register')
def upvote_post(request, pk, vote):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    user_profile = UserProfile.objects.get_or_create(user=post.author)[0]
    original_url = request.META.get('HTTP_REFERER', '/default/url/')
    
    if vote == 'U':
    # Check if the user has already upvoted this post, if they have undo upvote
        existing_vote = Vote.objects.filter(user=user, post=post).first()
        if existing_vote and existing_vote.vote_type == 'U':
            existing_vote.delete()
            post.score -= 1
            user_profile.karma -= 1
            post.save()
            user_profile.save()
            return redirect(original_url)
           
            #If there is an exisitng downvote, remove it, then add a new upvote
        elif existing_vote and existing_vote.vote_type == 'D':
            existing_vote.delete()
            post.score += 2
            user_profile.karma += 2
            post.save()
            user_profile.save()
            Vote.objects.create(user=user, post=post, vote_type='U')
            return redirect(original_url)
    # Otherwise create a new upvote
        else:
            Vote.objects.create(user=user, post=post, vote_type='U')
            post.score += 1
            post.save()
            user_profile.karma += 1
            user_profile.save()
            return redirect(original_url) 
    #Else vote is downvote
    else:
        existing_vote = Vote.objects.filter(user=user, post=post).first()
        #Check if there is an existing downvote, if so undo it
        if existing_vote and existing_vote.vote_type == 'D':
            existing_vote.delete()
            post.score += 1
            user_profile.karma += 1
            post.save()
            user_profile.save()
            return redirect(original_url) 
        
        #If there is an exisitng upvote, remove it, then add a downvote
        elif existing_vote and existing_vote.vote_type == 'U':
            existing_vote.delete()
            post.score -= 2
            user_profile.karma -= 2
            post.save()
            user_profile.save()
            Vote.objects.create(user=user, post=post, vote_type='D')
            return redirect(original_url)
        
        #Otherwise create a new downvote
        else:
            Vote.objects.create(user=user, post=post, vote_type='D')
            post.score -= 1
            post.save()
            user_profile.karma -= 1
            user_profile.save()
            return redirect(original_url) 
        
@login_required(login_url='register')
def delete_post(request, id, delete1, delete2):
    Post.objects.filter(id=id).delete()

    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    user_profile.num_posts -= 1
    user_profile.save()

    return redirect('/')
    
@login_required(login_url='register')
def delete_comment(request, id, delete1, delete2):
    original_url = request.META.get('HTTP_REFERER', '/default/url/')
    Response.objects.filter(id=id).delete()

    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    user_profile.num_comments -= 1
    user_profile.save()

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
                modified_comment = modify_comment(r.body)  # Call the function to modify the comment
                r.body = modified_comment
                r.save()
                user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
                user_profile.num_comments += 1
                user_profile.save()
                redirect('/post/' + str(post_id) + '/' + str(r.id))

        except Exception as e:
            raise e

    return redirect('/post/' + str(post_id) + '/' + str(r.id))

@login_required
def friends_list(request):
    user = request.user
    friends = user.userprofile.get_friends()
    return render(request, 'user_sidebar.html', {'friends': friends, 'user':user})

@login_required
def add_friend(request, friend_id):
    User = get_user_model()
    maybe_friend = get_object_or_404(User, id=friend_id)
    user_profile = request.user.userprofile

    # Check if already a friend
    if user_profile.friends.filter(id=maybe_friend.id).exists():
        # remove any pending friend requests
        try:
            user_profile.remove_friend_request(maybe_friend)
            maybe_friend.userprofile.remove_friend_request(request.user)
        except IntegrityError:
            # Prevent Database overlapped
            return HttpResponse(status=200)  # redirect('/profile/'+str(friend_id))
        return HttpResponse(status=200)#redirect('/profile/'+str(friend_id))

    # Otherwise add the friend
    try:
        user_profile.add_friend(maybe_friend)
        maybe_friend.userprofile.add_friend(request.user)
    except IntegrityError:
        # Prevent Database overlapped
        return HttpResponse(status=200)#redirect('/profile/'+str(friend_id))

    #remove any pending friend requests
    try:
        user_profile.remove_friend_request(maybe_friend)
        maybe_friend.userprofile.remove_friend_request(request.user)
    except IntegrityError:
        # Prevent Database overlapped
        return HttpResponse(status=200)  # redirect('/profile/'+str(friend_id))

    return HttpResponse(status=200)#redirect('/profile/'+str(friend_id))


@login_required
def send_friend_request(request, friend_id):
    User = get_user_model()
    maybe_friend = get_object_or_404(User, id=friend_id)
    user_profile = request.user.userprofile

    # Check if I've already received a friend request from this user.
    if user_profile.friend_requests.filter(id=maybe_friend.id).exists():
        #If so, immediately add as friend
        try:
            user_profile.add_friend(maybe_friend)
            maybe_friend.userprofile.add_friend(request.user)
        except IntegrityError:
            return HttpResponse(status=200)

        # remove any pending friend requests
        try:
            user_profile.remove_friend_request(maybe_friend)
            maybe_friend.userprofile.remove_friend_request(request.user)
        except IntegrityError:
            return HttpResponse(status=200)
        return HttpResponse(status=200)

    elif maybe_friend.userprofile.friend_requests.filter(id=request.user.id).exists():
        # Otherwise check if I've already sent a friend request. Do nothing if this is true
        return HttpResponse(status=200)

    # send a friend request
    try:
        maybe_friend.userprofile.add_friend_request(request.user)
    except IntegrityError:
        return HttpResponse(status=200)

    return HttpResponse(status=200)


@login_required
def reject_friend_request(request, friend_id):
    User = get_user_model()
    maybe_friend = get_object_or_404(User, id=friend_id)
    user_profile = request.user.userprofile

    # remove any pending friend requests between me and other user, if any
    try:
        maybe_friend.userprofile.remove_friend_request(request.user)
        user_profile.remove_friend_request(maybe_friend)
    except IntegrityError:
        return HttpResponse(status=200)

    return HttpResponse(status=200)

@login_required
def unfriend(request, friend_id):
    User = get_user_model()
    maybe_friend = get_object_or_404(User, id=friend_id)
    user_profile = request.user.userprofile

    # remove friend associations between me and other user
    try:
        maybe_friend.userprofile.remove_friend(request.user)
        user_profile.remove_friend(maybe_friend)
    except IntegrityError:
        return HttpResponse(status=200)

    return HttpResponse(status=200)

