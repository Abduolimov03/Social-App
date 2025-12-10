from django.urls import path
from posts.views import PostLikeToggleApi, PostCreateApi, PostListApi, CommentCreateApi, CommentLikeToggleApi, FeedApi, \
    PostBookmarkToggleApi

urlpatterns = [
    path('post/create/', PostCreateApi.as_view()),
    path('posts/', PostListApi.as_view()),
    path('posts/<int:post_id>/like/', PostLikeToggleApi.as_view()),
    path('comment/create/', CommentCreateApi.as_view()),
    path('comments/<int:comment_id>/like/', CommentLikeToggleApi.as_view()),
    path('feed/', FeedApi.as_view()),
    path('posts/<int:post_id>/bookmark/', PostBookmarkToggleApi.as_view()),



]
