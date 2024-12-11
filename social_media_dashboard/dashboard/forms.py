from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    api_key = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter your Graph API Key"}),
        help_text="Your API key is required to fetch posts.",
    )
    instagram_user_id = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter your Instagram User ID"}),
        help_text="This is required to fetch your Instagram posts.",
    )

    class Meta:
        model = CustomUser
        fields = ["username", "password1", "password2", "api_key", "instagram_user_id"]
