from django.db import models
from django.contrib.auth.models import User


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

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/', verbose_name='Video file')
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    is_short = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_views(self):
        return humanize_number(self.views)

class VideoView(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
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