from django import forms
from .models import Post, Comment
from .forms_user import *


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
