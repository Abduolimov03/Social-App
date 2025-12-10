from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import PostCreateSerializer
from rest_framework.generics import ListAPIView
from .models import Post
from .serializers import PostListSerializer
from .models import  PostLike
from .serializers import CommentCreateSerializer




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

        if like_obj:
            like_obj.delete()
            return Response({"liked": False, "message": "Unliked"}, status=200)
        else:
            PostLike.objects.create(post=post, user=user)
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

