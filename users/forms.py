from .models import CustomUser
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()
    display_name = forms.CharField(
        max_length=20,
        help_text='A publicly displayed name. Does not need to be unique.')

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email', 'display_name', 'password1', 'password2',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'display_name', 'password',)
