from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Post, Response, Topic, UserProfile


class RegisterUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs = {'placeholder': 'password'}
        self.fields['password2'].widget.attrs = {'placeholder': 'confirm password'}

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]
        widgets = {
            'email': forms.EmailInput(attrs={
                'required': True,
                'placeholder': 'sample@example.com',
                'autofocus': True
            }),
            'username': forms.TextInput(attrs={
                'placeholder': 'sample: Jack',
            })
        }


class LoginForm(AuthenticationForm):
    class Meta:
        fields = ["__all__"]


class EditBioForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['topic', 'title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={
                'autofocus': True,
                'placeholder': 'Your title'
            })
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['body']


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'autofocus': True,
                'placeholder': 'Your title'
            })
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'placeholder': "Put in your comments.",
            })
        }
