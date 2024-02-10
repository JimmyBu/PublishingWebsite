from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.views.generic import *
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .forms_user import EditBioForm, RegisterUserForm, LoginForm
from .models_user import UserProfile


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
    return render(request, 'register.html', context)


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

