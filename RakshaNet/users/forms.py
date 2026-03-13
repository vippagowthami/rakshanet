from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        widget=forms.RadioSelect(),
        label="Select Your Role",
        help_text="Choose 1 if you're an Admin/NGO, 2 if you're a Volunteer, 3 if you need help"
    )
    
    class Meta:
        model = User
        fields = ["username", 'email', 'role', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = '• Your password must contain at least 8 characters.\n• Your password can\'t be a commonly used password.\n• Your password can\'t be entirely numeric.'
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile 
        fields = ['image']