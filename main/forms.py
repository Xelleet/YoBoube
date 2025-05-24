from django import forms
from .models import Video, Reels
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, Comment

class VideoForm(forms.ModelForm):
    video_file = forms.FileField()

    class Meta:
        model = Video
        fields = ['title', 'video_file']

class ReelsForm(forms.ModelForm):
    class Meta:
        model = Reels
        fields = ['title', 'video_file']

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class SubscribeForm(forms.Form):
    channel_id = forms.IntegerField(widget=forms.HiddenInput())