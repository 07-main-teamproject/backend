from django.urls import path
from .views import SignUpAPIView, LoginAPIView, LogoutAPIView, UserInfoAPIView
from django.http import JsonResponse

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
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path('info/<int:pk>/', UserInfoAPIView.as_view(), name='user-info'),
]