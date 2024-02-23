from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm
from .models import ChatMessage, Profile


class ChatMessageForm(ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={"class": "forms", "rows": 3, "placeholder": "Type in your "
                                                                                                    "message"}))

    class Meta:
        model = ChatMessage
        fields = [
            "body",
        ]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'pic']
