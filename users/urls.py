from .views import SignUpView, VerifyCodeApiView, GetNewCodeVerify, ChangeInfoUserApi, TokenRefreshApi
from django.urls import path

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('verify/', VerifyCodeApiView.as_view()),
    path('new-verify/', GetNewCodeVerify.as_view()),
    path('change-info/', ChangeInfoUserApi.as_view()),
    path("token-refresh/", TokenRefreshApi.as_view()),

]