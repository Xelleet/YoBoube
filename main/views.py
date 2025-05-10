from django.shortcuts import render, redirect
from .models import Video, Profile
from .forms import VideoForm, RegisterForm
from django.contrib.auth.decorators import login_required

#user = request.user
#profile = user.profile

def video_list(request):
    videos = Video.objects.all()
    return render(request, 'video_list.html', {'videos': videos, 'user': request.user})

def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('video_list')
    else:
        form = VideoForm()

    return render(request, 'upload_video.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def profile(request):
    if request.user.is_authenticated:
        return render(request, 'Profile.html', {'profile': Profile.objects.get(user=request.user)})
    else:
        return redirect('login')