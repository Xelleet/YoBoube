from django.shortcuts import render, redirect, get_object_or_404
from .models import Video, Profile, Like, Comment, CommentLike, Reels, VideoView, Subscription, User
from .forms import VideoForm, RegisterForm, ProfileForm, CommentForm, ReelsForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt #Для продакшена это самоубийство, по ходу времени лучше снести
from django.db.models import F, Value, IntegerField
from django.db.models.functions import Coalesce
from django.db.models import ExpressionWrapper, FloatField
from ffprobe import FFProbe
import os


#Наши видео и прости господи шортсы
def video_list(request):
    videos = Video.objects.annotate(rating=F('likes_count') - F('dislikes_count')).order_by('-rating').filter(is_short=False) #Составляем рекомендации (у нас нет алгоритмов гугла, так что выглядит колхозно
    reels = Video.objects.annotate(rating=F('likes_count') - F('dislikes_count')).order_by('-rating').filter(is_short=True)
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        profile = None #В случае, если мы ещё не зарегистрированы, или же вышли из аккаунта
    return render(request, 'video_list.html', {'videos': videos, 'reels': reels, 'profile': profile})

def reels_list(request):
    reels = Video.objects.filter(is_short=True)
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        profile = None #В случае, если мы ещё не зарегистрированы, или же вышли из аккаунта
    return render(request, 'Reels.html', {'reels': reels, 'profile': profile})


#Система выкладывания нашего ужаса
def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = request.FILES['video_file']
            temp_path = 'temp_reel_video.mp4'

            video.uploader = request.user

            with open(temp_path, 'wb+') as destination:
                for chunk in video.chunks():
                    destination.write(chunk)

            try:
                info = FFProbe(temp_path)
                duration = None

                for stream in info.streams:
                    if stream.is_video():
                        duration = float(stream.duration_seconds())
                        print(f"Duration: {duration}s")  # Для отладки

                        if duration > 60:
                            form.instance.is_short = False
                        else:
                            form.instance.is_short = True
                        break

                if duration is None:
                    raise ValueError("Видеопоток не найден в файле")

            except Exception as e:
                print(f"Reels error: {e}")

            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            form.instance.uploader = request.user
            form.save()
            return redirect('video_list')
    else:
        form = VideoForm()

    return render(request, 'upload_video.html', {'form': form})


#Профиль
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

@login_required()
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile', user_id=profile.id)
    else:
        form = ProfileForm()
    return render(request, 'edit_profile.html', {'form': form})

#Лепим лайки
@csrf_exempt #Временно
@login_required
def toggle_like(request, pk):
    video = get_object_or_404(Video, id=pk)
    user = request.user
    reaction_type = request.POST.get('reaction_type')

    reaction = Like.objects.filter(user=user, video=video).first()

    #Меняем кол-во лайков и/или дизлайков в зависимости от текущей реакции на видео
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


#Страница самого видео со всей информацией
def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    session_key = request.session.session_key or request.COOKIES.get('sessionid')
    if session_key and not VideoView.objects.filter(video=video, session_key=session_key).exists():
        #Добавляем просмотры к видео, если у нас "уникальный" пользователь (чтобы как в VK видео не было)
        VideoView.objects.create(video=video, session_key=session_key)
        video.views += 1
        video.save(update_fields=['views'])
    comments = video.comments.all()

    WEIGHT_VIEWS = 0.01 #Цена или вес просмотра (чтобы новички на платформе имели шансы попасть в рекомендации например)

    suggested_videos = Video.objects.exclude(pk=pk).annotate(
        rating=ExpressionWrapper(
            F('likes_count') - F('dislikes_count') + WEIGHT_VIEWS * F('views'),
            output_field=FloatField()
        )
    ).order_by('-rating').filter(is_short=False)[:10]
    #Проверяем, поставили ли мы уже реакцию на видео
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

    is_subscribed = False
    if request.user.is_authenticated and request.user != video.uploader:
        is_subscribed = video.uploader.subscribers.filter(subscriber=request.user).exists()

    #Если мы хотим оставить свой чудесный комментарий
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
    return render(request, 'video_detail.html', {'video': video, 'comments': comments, 'form': form, 'is_liked': is_liked, 'is_disliked': is_disliked, 'suggested_videos': suggested_videos, 'is_subscribed': is_subscribed})

def reel(request, pk):
    return pk #ToDO сделать логику рилсов

def delete_video(request, pk):
    video = get_object_or_404(Video, id=pk)
    video.delete() #ToDO: Я так прикинул, нам надо ещё и с сервера файл видео сносить
    return redirect('video_list')

def search_videos(request):
    query = request.GET.get('q')
    if query:
        videos = Video.objects.filter(title__icontains=query).annotate(rating=F('likes_count') - F('dislikes_count')).order_by('-rating')
    else:
        videos = Video.objects.annotate(rating=F('likes_count') - F('dislikes_count')).order_by('-rating')
    return render(request, 'search_result.html', {'videos': videos})

@login_required()
def toggle_subscription(request, user_id):
    channel = get_object_or_404(User, id=user_id)

    if request.user == channel:
        return redirect('profile')

    subscription, created = Subscription.objects.get_or_create(subscriber=request.user, channel=channel)

    if not created:
        subscription.delete()

    return redirect('user_profile', user_id=channel.id)

def user_profile(request, user_id):
    profile = Profile.objects.get(id=user_id)
    subs = Subscription.objects.filter(subscriber_id=profile.user.id)
    is_subscribed = False
    if request.user.is_authenticated and request.user != profile:
        is_subscribed = profile.user.subscribers.filter(subscriber=request.user).exists()
    return render(request, 'user_profile.html', {'user': request.user,'profile': Profile.objects.get(user=request.user), 'user_profile': Profile.objects.get(id=user_id), 'is_subscribed': is_subscribed, 'subs': subs})