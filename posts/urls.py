from django.urls import path
from posts.views import PostLikeToggleApi, PostCreateApi, PostListApi

urlpatterns = [
    path('post/create/', PostCreateApi.as_view()),
    path('posts/', PostListApi.as_view()),
    path('posts/<int:post_id>/like/', PostLikeToggleApi.as_view()),
]
