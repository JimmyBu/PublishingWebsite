from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from .models_user import UserProfile

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