from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import SignUpAPIView, LoginAPIView, LogoutAPIView, ProfileView, MyUserInfoAPIView
from django.http import JsonResponse
from .social import GoogleLoginAPIView, KakaoLoginAPIView, NaverLoginAPIView

# 기본 응답 뷰
def users_root(request):
    return JsonResponse({
        "message": "사용 가능한 엔드포인트 목록",
        "endpoints": [
            "/users/signup/",
            "/users/login/",
            "/users/logout/",
            "/info/<int:pk>/"
        ]
    })

urlpatterns = [
    path("", users_root, name="users_root"),
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("new_login/",TokenObtainPairView.as_view(), name="new_login"),
    path("token_refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path('me/', MyUserInfoAPIView.as_view(), name='my-info'),

    path("profile/",ProfileView.as_view(), name='profile'),

# ✅ 소셜 로그인 추가
    path("social/google/", GoogleLoginAPIView.as_view(), name="google-login"),
    path("social/kakao/", KakaoLoginAPIView.as_view(), name="kakao-login"),
    path("social/naver/", NaverLoginAPIView.as_view(), name="naver-login"),
]