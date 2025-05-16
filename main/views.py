from django.shortcuts import render, redirect, get_object_or_404
from .models import Video, Profile, Like, Comment, CommentLike
from .forms import VideoForm, RegisterForm, ProfileForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt #Для продакшена это самоубийство, по ходу времени лучше снести


@login_required() #Временно
def video_list(request):
    videos = Video.objects.all()
    return render(request, 'video_list.html', {'videos': videos, 'profile': Profile.objects.get(user=request.user)})

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

@login_required()
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm()
    return render(request, 'edit_profile.html', {'form': form})

@csrf_exempt
@login_required
def toggle_like(request, pk):
    video = get_object_or_404(Video, id=pk)
    user = request.user
    reaction_type = request.POST.get('reaction_type')

    reaction = Like.objects.filter(user=user, video=video).first()

    #К сожалению мне слишком впадлу менять эту логику с дофига elif, так что имеем что имеем
    if request.method == 'POST':
        if reaction:
            if reaction.reaction_type == reaction_type:
                if reaction_type == 'like':
                    video.likes_count -= 1
                    video.save()
                elif reaction_type == 'dislike':
                    video.dislikes_count -= 1
                    video.save()
                reaction.delete()
            else:
                reaction.reaction_type = reaction_type
                if reaction_type == 'like':
                    video.likes_count += 1
                    video.dislikes_count -= 1
                    video.save()
                elif reaction_type == 'dislike':
                    video.likes_count -= 1
                    video.dislikes_count += 1
                    video.save()
                reaction.save()
        else:
            Like.objects.create(user=user, video=video, reaction_type=reaction_type)
            if reaction_type == 'like':
                video.likes_count += 1
                video.save()
            elif reaction_type == 'dislike':
                video.dislikes_count += 1
                video.save()

    video.save()
    return redirect('video_detail', pk)

@csrf_exempt
@login_required()
def toggle_comment_like(request, pk, id):
    video = get_object_or_404(Video, id=id)
    comment = get_object_or_404(Comment, id=pk, video=video)
    user = request.user

    if request.method == 'POST':
        like = CommentLike.objects.filter(user=user, comment=comment).first()
        if like != None:
            comment.likes_count -= 1
            like.delete()
        else:
            comment.likes_count += 1
            CommentLike.objects.create(user=user, comment=comment)
        comment.save()

    return redirect('video_detail', pk)


def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    comments = video.comments.all()
    try:
        like = Like.objects.get(user_id=request.user.id, video_id=pk)
        if like.reaction_type == 'like':#Как бы дебильно это не выглядело
            is_liked = True
            is_disliked = False
        else:
            is_disliked = True
            is_liked = False
    except:
        is_liked = False
        is_disliked = False


    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.video = video
                comment.user = request.user
                comment.save()
                return redirect('video_detail', pk=pk)
        else:
            return redirect('login')
    else:
        form = CommentForm()
    return render(request, 'video_detail.html', {'video': video, 'comments': comments, 'form': form, 'is_liked': is_liked, 'is_disliked': is_disliked})

def delete_video(request, pk):
    video = get_object_or_404(Video, id=pk)
    video.delete()
    return redirect('video_list')