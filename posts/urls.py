from django.urls import path
from posts.views import PostCreateApi

urlpatterns = [
    path('post/create/', PostCreateApi.as_view()),
]
