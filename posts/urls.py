from django.urls import path
from posts.views import PostListApi, PostCreateApi

urlpatterns = [
    path('post/create/', PostCreateApi.as_view()),
    path('posts/', PostListApi.as_view()),
]
