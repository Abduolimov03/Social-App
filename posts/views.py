from django.db.migrations import serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, request
from .serializers import PostCreateSerializer, CommentListSerializer
from .models import Post, Comment, CommentLike
from .models import  PostLike
from .serializers import CommentCreateSerializer
from .pagination import CommentPagination
from rest_framework.exceptions import PermissionDenied
from notifications.utils import create_notification
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import PostListSerializer
from users.models import UserFollow
from .models import SavedPost

class PostCreateApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PostCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        return Response({
            "message": "Post created successfully",
            "post_id": post.id
        }, status=status.HTTP_201_CREATED)

    post = serializer.save()

    from notifications.utils import create_mentions
    if post.caption:
        create_mentions(sender=request.user, text=post.caption, post=post)


class PostListApi(ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return (
            Post.objects.filter(is_active=True)
            .select_related("user")
            .prefetch_related("media", "likes", "comments")
            .order_by("-created_at")
        )





class PostLikeToggleApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        user = request.user

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=404)

        like_obj = PostLike.objects.filter(post=post, user=user).first()


        # Like qilingan joyda
        if like_obj:
            like_obj.delete()
            return Response({"liked": False, "message": "Unliked"}, status=200)
        else:
            PostLike.objects.create(post=post, user=user)
            create_notification(
                sender=user,
                recipient=post.user,
                notif_type='like',
                post=post,
                message=f"{user.username} sizning postingizni like qildi"
            )
            return Response({"liked": True, "message": "Liked"}, status=201)


class CommentCreateApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CommentCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        return Response(
            {
                "message": "Comment created",
                "comment_id": comment.id
            },
            status=status.HTTP_201_CREATED
        )


    serializer_class = CommentListSerializer
    permission_classes = [permissions.AllowAny]

    comment = serializer.save()

    create_notification(
        sender=request.user,
        recipient=comment.post.user,
        notif_type='comment',
        post=comment.post,
        comment=comment,
        message=f"{request.user.username} sizning postingizga comment qoldirdi"
    )

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return (
            Comment.objects
            .filter(post_id=post_id, parent__isnull=True)
            .select_related('user')
            .prefetch_related('replies')
            .order_by('created_at')
        )


    # Post egasiga comment notification

    # Mention notification
    from notifications.utils import create_mentions
    create_mentions(sender=request.user, text=comment.text, post=comment.post, comment=comment)



class CommentListApi(ListAPIView):
    serializer_class = CommentListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CommentPagination

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return (
            Comment.objects
            .filter(post_id=post_id, parent__isnull=True)
            .select_related('user')
            .prefetch_related('replies')
            .order_by('created_at')
        )


class CommentDeleteApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment topilmadi"}, status=404)

        if comment.user != request.user:
            raise PermissionDenied("Siz bu commentni o‘chira olmaysiz")

        comment.delete()
        return Response(
            {"message": "Comment o‘chirildi"},
            status=status.HTTP_200_OK
        )


class CommentLikeToggleApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        user = request.user

        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment topilmadi"}, status=404)

        like = CommentLike.objects.filter(comment=comment, user=user).first()

        if like:
            like.delete()
            return Response({"liked": False}, status=200)
        else:
            CommentLike.objects.create(comment=comment, user=user)
            return Response({"liked": True}, status=201)





class FeedApi(ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Faqat follow qilganlar postlari
        following_ids = user.following.values_list('following_id', flat=True)
        return Post.objects.filter(user_id__in=following_ids, is_active=True).order_by('-created_at')





class PostBookmarkToggleApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        user = request.user
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post topilmadi"}, status=404)

        saved = SavedPost.objects.filter(user=user, post=post).first()
        if saved:
            saved.delete()
            return Response({"saved": False}, status=200)
        else:
            SavedPost.objects.create(user=user, post=post)
            return Response({"saved": True}, status=201)
