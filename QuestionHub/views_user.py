from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import *
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .forms import SignupForm


@login_required
def user_profile_self(request):
    """
    view for user's own profile page
    :param request:html request
    :return:
    """
    current_user = request.user
    if current_user.is_authenticated:
        return render(request, 'registration/self_user_detail.html', context={'user': current_user})
    else:
        return redirect("login")


def user_profile(request, primary_key):
    """
    view for general user profile
    :param request:
    :param primary_key:
    :return:
    """
    User = get_user_model()

    if primary_key == request.user.id:
        return redirect("user_profile_self")

    trgt_user = get_object_or_404(User, pk=primary_key)
    return render(request, 'registration/user_detail.html', context={'user': trgt_user})



class CreateUser(CreateView):
    """
    Class-based view for the sign up page
    """
    form_class = SignupForm
    model = get_user_model()
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
