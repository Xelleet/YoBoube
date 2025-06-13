from django import forms
from .models import Video, Reels, Category, Report, PlayList
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, Comment

class VideoForm(forms.ModelForm):
    video_file = forms.FileField()
    tags = forms.CharField(
        required=False,
        help_text="Enter tags",
        widget=forms.TextInput(attrs={'placeholder': 'Tag1, Tag2, Tag3'})
    )

    class Meta:
        model = Video
        fields = ['title', 'video_file', 'preview', 'category']

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects

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

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = PlayList
        fields = ['name']