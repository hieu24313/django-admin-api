from django.db.models import Q
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.blog.models import Blog, Comment, ReplyComment
from apps.blog.serializers import BlogSerializer, CommentSerializer, ReplyCommentSerializer
from apps.user.models import FriendShip
from ultis.api_helper import api_decorator


class GetBlogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        serializer = BlogSerializer(Blog.objects.filter(is_active=True).order_by('-created_at'), many=True,
                                    context={'request': request})
        return serializer.data, 'Toàn bộ bài đăng!', status.HTTP_200_OK


class GetBlogProposalAPIView(
    APIView):  # lấy bài viết đề xuất theo mục "đề xuất (like và comment cao)" theo TOK FeatureList
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        queryset = Blog.objects.filter(is_active=True).order_by('-count_like', '-count_comment')
        serializer = BlogSerializer(queryset, many=True, context={'request': request})
        return serializer.data, 'Bài đăng đề xuất!', status.HTTP_200_OK


class GetBlogInterestAPIView(APIView):  # lấy bài viết của bạn bè mục "quan tâm" theo TOK FeatureList
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        accepted_friendships = FriendShip.objects.filter(
            Q(sender=request.user, status='accepted') | Q(receiver=request.user, status='accepted')
        )
        related_users = []
        for friendship in accepted_friendships:
            if friendship.sender == request.user:
                # Nếu user là sender, lấy thông tin receiver của FriendShip
                related_users.append(friendship.receiver)
            elif friendship.receiver == request.user:
                # Nếu user là receiver, lấy thông tin sender của FriendShip
                related_users.append(friendship.sender)
        blogs = Blog.objects.filter(user__in=related_users, is_active=True)

        serializer = BlogSerializer(blogs, many=True, context={'request': request})
        return serializer.data, 'Bài viết của bạn bè!', status.HTTP_200_OK


class BlogDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request, pk):
        try:
            serializer = BlogSerializer(Blog.objects.get(id=pk, is_active=True), context={'request': request})
            return serializer.data, 'Chi tiết bài đăng', status.HTTP_200_OK
        except:
            return {}, 'Bài đăng không tồn tại hoặc đã bị xóa!', status.HTTP_400_BAD_REQUEST


class CreateBlogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        number_of_files = len(request.data.get("file", []))
        # print(number_of_files)
        if int(number_of_files) > 9:
            return {}, 'Vượt quá số hình cho phép!', status.HTTP_400_BAD_REQUEST
        else:
            request.data['user'] = str(request.user.id)
            serializer = BlogSerializer(data=request.data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return serializer.data, 'Tạo bài đăng thành công!', status.HTTP_200_OK


class UpdateBlogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def put(self, request, pk):
        try:
            blog = Blog.objects.get(id=pk, is_active=True)
        except:
            return {}, 'Bài đăng không tồn tại!', status.HTTP_400_BAD_REQUEST
        # request.data['user'] = str(request.user.id)
        serializer = BlogSerializer(blog, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return serializer.data, 'Cập nhật bài đăng thành công!', status.HTTP_200_OK


class DeleteBlogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def delete(self, request, pk):
        try:
            blog = Blog.objects.get(id=pk, is_active=True)
            blog.is_active = False
            blog.save()
            return {}, 'Xóa bài đăng thành công!', status.HTTP_204_NO_CONTENT
        except:
            return {}, 'Bài đăng không tồn tại hoặc đã bị xóa!', status.HTTP_400_BAD_REQUEST


class LikeBlogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        blog_id = request.data.get('blog_id')
        try:
            blog = Blog.objects.get(id=blog_id)
        except:
            return {}, 'Bài đăng không tồn tại hoặc đã bị xóa!', status.HTTP_400_BAD_REQUEST

        check_exists = blog.user_like.filter(id=request.user.id).exists()
        if check_exists:
            return {}, 'Đã yêu thích rồi!', status.HTTP_400_BAD_REQUEST
        else:
            blog.count_like += 1
            blog.user_like.add(request.user)
            blog.save()
            return {}, 'Đã yêu thích bài đăng!', status.HTTP_200_OK


class UnLikeBlogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        blog_id = request.data.get('blog_id')
        try:
            blog = Blog.objects.get(id=blog_id)
        except:
            return {}, 'Bài đăng không tồn tại hoặc đã bị xóa!', status.HTTP_400_BAD_REQUEST

        check_exists = blog.user_like.filter(id=request.user.id).exists()
        if check_exists:
            blog.count_like -= 1
            blog.user_like.remove(request.user)
            blog.save()
            return {}, 'Đã hủy yêu thích bài đăng!', status.HTTP_204_NO_CONTENT
        else:
            return {}, 'Chưa yêu thích bài đăng!', status.HTTP_400_BAD_REQUEST


class GetCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request, pk):
        serializer = CommentSerializer(Comment.objects.filter(blog_id=pk, is_active=True), many=True,
                                       context={'request': request})
        return serializer.data, 'Bình luận của 1 bài đăng!', status.HTTP_200_OK


class CreateCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        request.data['user'] = str(request.user.id)
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            blog_id = request.data.get('blog')
            blog = Blog.objects.get(id=blog_id)
            blog.count_comment += 1
            blog.save()
        return serializer.data, 'Thêm bình luận thành công!', status.HTTP_200_OK


class UpdateCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def put(self, request, pk):
        request.data['user'] = str(request.user.id)
        # blog_id = request.data.get('blog')
        # blog = Blog.objects.get(id=blog_id)
        comment = Comment.objects.get(id=pk)
        serializer = CommentSerializer(comment, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return serializer.data, 'Cập nhật bình luận thành công!', status.HTTP_200_OK


class DeleteCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(id=pk, is_active=True)
        except:
            return {}, 'Comment không tồn tại!', status.HTTP_400_BAD_REQUEST

        comment.blog.count_comment -= 1
        comment.blog.save()

        comment.is_active = False
        comment.save()

        return {}, 'Xóa thành công!', status.HTTP_204_NO_CONTENT


class LikeCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        comment_id = request.data.get('comment_id')
        try:
            comment = Comment.objects.get(id=comment_id)
            if not comment.user_like.filter(id=request.user.id).exists():
                comment.count_like += 1
                comment.user_like.add(request.user)
                comment.save()
                return {}, 'Đã yêu thích bình luận này!', status.HTTP_200_OK
            else:
                return {}, 'Bạn đã yêu thích bình luận này rồi!', status.HTTP_400_BAD_REQUEST

        except:
            return {}, 'Bình luận không tồn tại!', status.HTTP_400_BAD_REQUEST


class UnLikeCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        comment_id = request.data.get('comment_id')
        try:
            comment = Comment.objects.get(id=comment_id)
            if comment.user_like.filter(id=request.user.id).exists():
                comment.count_like -= 1
                comment.user_like.remove(request.user)
                comment.save()
                return {}, 'Hủy yêu thích!', status.HTTP_200_OK
            else:
                return {}, 'Chưa yêu thích!', status.HTTP_400_BAD_REQUEST

        except:
            return {}, 'Bình luận không tồn tại!', status.HTTP_400_BAD_REQUEST


class GetReplyCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request, pk):
        queryset = ReplyComment.objects.filter(comment_id=pk)
        serializer = ReplyCommentSerializer(queryset, many=True, context={'request': request})
        return serializer.data, 'Các phản hồi của bình luận!', status.HTTP_200_OK


class AddReplyCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        request.data['user'] = str(request.user.id)
        serializer = ReplyCommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return serializer.data, 'Phản hồi bình luận thành công!', status.HTTP_200_OK


class UpdateReplyCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def put(self, request, pk):
        try:
            reply_comment = ReplyComment.objects.get(id=pk)
        except:
            return {}, 'Phản hồi này không tồn tại!', status.HTTP_400_BAD_REQUEST
        serializer = ReplyCommentSerializer(reply_comment, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return serializer.data, 'Cập nhật phản hồi bình luận thành công!', status.HTTP_200_OK


class DeleteReplyCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def delete(self, request, pk):
        try:
            reply_comment = ReplyComment.objects.get(id=pk)
            reply_comment.is_active = False
            reply_comment.save()
            return {}, 'Xóa bình luận thành công!', status.HTTP_204_NO_CONTENT
        except:
            return {}, 'Bình luận không tồn tại!', status.HTTP_400_BAD_REQUEST