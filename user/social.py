import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from user.models import User


class GoogleLoginAPIView(APIView):
    def post(self, request):
        code = request.data.get("code")

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        }

        response = requests.post(token_url, data=data)
        token_data = response.json()

        if "access_token" not in token_data:
            return Response({"error": "Invalid authorization code"}, status=status.HTTP_400_BAD_REQUEST)

        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        user_info_response = requests.get(user_info_url, headers={"Authorization": f"Bearer {token_data['access_token']}"})
        user_info = user_info_response.json()

        email = user_info.get("email")
        name = user_info.get("name")

        user, created = User.objects.get_or_create(email=email, defaults={"name": name})

        refresh = RefreshToken.for_user(user)

        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "message": "구글 로그인 성공"
        })


class KakaoLoginAPIView(APIView):
    def post(self, request):
        code = request.data.get("code")

        token_url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "client_secret": settings.KAKAO_CLIENT_SECRET,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        }

        response = requests.post(token_url, data=data)
        token_data = response.json()

        if "access_token" not in token_data:
            return Response({"error": "Invalid authorization code"}, status=status.HTTP_400_BAD_REQUEST)

        user_info_url = "https://kapi.kakao.com/v2/user/me"
        user_info_response = requests.get(user_info_url, headers={"Authorization": f"Bearer {token_data['access_token']}"})
        user_info = user_info_response.json()

        email = user_info.get("kakao_account", {}).get("email")
        name = user_info.get("properties", {}).get("nickname")

        user, created = User.objects.get_or_create(email=email, defaults={"name": name})

        refresh = RefreshToken.for_user(user)

        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "message": "카카오 로그인 성공"
        })


class NaverLoginAPIView(APIView):
    def post(self, request):
        code = request.data.get("code")
        state = request.data.get("state")

        token_url = "https://nid.naver.com/oauth2.0/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_CLIENT_SECRET,
            "code": code,
            "state": state,
        }

        response = requests.post(token_url, data=data)
        token_data = response.json()

        if "access_token" not in token_data:
            return Response({"error": "Invalid authorization code"}, status=status.HTTP_400_BAD_REQUEST)

        user_info_url = "https://openapi.naver.com/v1/nid/me"
        user_info_response = requests.get(user_info_url, headers={"Authorization": f"Bearer {token_data['access_token']}"})
        user_info = user_info_response.json()

        email = user_info.get("response", {}).get("email")
        name = user_info.get("response", {}).get("name")

        user, created = User.objects.get_or_create(email=email, defaults={"name": name})

        refresh = RefreshToken.for_user(user)

        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "message": "네이버 로그인 성공"
        })
