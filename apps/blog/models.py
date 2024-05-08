import uuid

from django.db import models

from apps.general.models import FileUpload
from apps.user.models import CustomUser


class Blog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    content = models.TextField(null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owner')

    tagged_users = models.ManyToManyField(CustomUser, related_name='tagged_in', blank=True)

    count_comment = models.PositiveIntegerField(default=0)
    count_like = models.PositiveIntegerField(default=0)
    count_share = models.PositiveIntegerField(default=0)

    location = models.CharField(max_length=50, null=True, blank=True)

    # user_like = models.ManyToManyField(CustomUser, blank=True)
    file = models.ManyToManyField(FileUpload, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


class LikeBlog(models.Model):
    TYPE_CHOICES = (
        ('LIKE', 'LIKE'),
        ('UNLIKE', 'UNLIKE')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    type = models.CharField(choices=TYPE_CHOICES, default='LIKE', max_length=6)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    content = models.TextField(null=True, blank=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owner_comment')
    count_like = models.PositiveIntegerField(default=0)

    # user_like = models.ManyToManyField(CustomUser, blank=True)
    file = models.ManyToManyField(FileUpload, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


class LikeComment(models.Model):
    TYPE_CHOICES = (
        ('LIKE', 'LIKE'),
        ('UNLIKE', 'UNLIKE')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    type = models.CharField(choices=TYPE_CHOICES, default='LIKE', max_length=6)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ReplyComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    content = models.TextField(null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owner_reply_comment')
    count_like = models.PositiveIntegerField(default=0)
    # user_like = models.ManyToManyField(CustomUser, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


class LikeReplyComment(models.Model):
    TYPE_CHOICES = (
        ('LIKE', 'LIKE'),
        ('UNLIKE', 'UNLIKE')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    type = models.CharField(choices=TYPE_CHOICES, default='LIKE', max_length=6)
    reply_comment = models.ForeignKey(ReplyComment, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)