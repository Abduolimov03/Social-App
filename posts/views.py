from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import PostCreateSerializer
from rest_framework.generics import ListAPIView
from rest_framework import permissions
from .models import Post
from .serializers import PostListSerializer


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
