from rest_framework import serializers

from apps.blog.models import Blog, Comment, ReplyComment
from apps.general.serializers import GetFileUploadSerializer
from apps.user.models import CustomUser


class UserBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id',
                  'full_name',
                  'avatar']


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserBlogSerializer(instance.user).data
        data['user_like'] = UserBlogSerializer(instance.user_like, many=True).data
        data['file'] = GetFileUploadSerializer(instance.file, many=True).data

        check_exists = instance.user_like.filter(id=self.context['request'].user.id).exists()
        if check_exists:
            data['liked'] = True
        else:
            data['liked'] = False

        data['comment'] = CommentSerializer(Comment.objects.filter(blog=instance, is_active=True), many=True, context=self.context).data

        return data


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserBlogSerializer(instance.user).data
        data['file'] = GetFileUploadSerializer(instance.file, many=True).data

        return data


class ReplyCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplyComment
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['user'] = UserBlogSerializer(instance.user).data
        return data