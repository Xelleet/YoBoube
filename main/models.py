from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def humanize_number(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value

    if value >= 1000000:
        return f"{value / 1000000:.1f} млн".replace(".0", "")
    elif value >= 1000:
        return f"{value / 1000:.1f} тыс".replace(".0", "")
    else:
        return str(value)


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/', verbose_name='Video file')
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    is_short = models.BooleanField(default=False)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_videos', null=True, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    preview = models.ImageField(upload_to='previews/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    deleted = models.BooleanField(default=False)

    def get_uploaded_at(self):
        from django.utils.timesince import timesince
        return f"{timesince(self.uploaded_at)} назад"

    def __str__(self):
        return self.title

    def get_views(self):
        return humanize_number(self.views)

class VideoView(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='video')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

class Reels(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='reels/', verbose_name='Reels file')
    likes_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class Like(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    REACTION_TYPES = (
        (LIKE, '👍'),
        (DISLIKE, '👎'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=7, choices=REACTION_TYPES, default="👍")

    class Meta:
        unique_together = ('user', 'video')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f'Profile {self.user.username}'

class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Comment from {self.user.username} to {self.video.title}"

class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'comment')

class Subscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    channel = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'channel')

    def __str__(self):
        return f"{self.subscriber.username} подписан на {self.channel.username}"

class WatchLater(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meeta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f"{self.user.username} - {self.video.title}"

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.query}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = (
        ('pending', 'В обработке'),
        ('processed', 'Обработано'),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        target = self.video if self.video else self.comment
        return f"Жалоба от {self.user.username} на {target} ({self.get_status_display()})"

    def get_status_display(self):
        return self.status

class PlayList(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    videos = models.ManyToManyField(Video, through='PlaylistItem')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PlaylistItem(models.Model):
    playlist = models.ForeignKey(PlayList, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.playlist.name}: {self.video.title}"