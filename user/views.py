from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from .models import User,Profile
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, UserUpdateSerializer, ProfileSerializer
from django.core.files.base import ContentFile
import base64


# 회원가입 api
class SignUpAPIView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 가능

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)  # 사용자 데이터 검증 및 저장
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)

        # serializer.is_valid()가 False인 경우, errors를 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 로그인 api
class LoginAPIView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 가능하게 해주는 api

    def post(self, request):
        serializer = LoginSerializer(data=request.data)  # 사용자 정보 검증 후 JWT토큰 발급

        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)

            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 로그아웃 api
class LogoutAPIView(APIView):
    permission_classes = [AllowAny]  # 인증된 사용자만 접근

    def post(self, request):

        try:
            # 클라이언트의 쿠키 삭제
            response = Response({"message": "로그아웃 되었습니다."}, status=status.HTTP_200_OK)
            response.delete_cookie("access_token")  # Access Token 삭제
            response.delete_cookie("refresh_token")  # Refresh Token 삭제
            return response
        except Exception as e:
            # 예외 처리 로직 단순화
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MyUserInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # 로그인한 사용자
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        # 본인 계정만 수정 가능하도록 제한
        if request.user.pk != pk:
            raise PermissionDenied('본인의 정보만 수정할 수 있습니다.')

        user = get_object_or_404(User, pk=pk)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        print(f"Deleting user with id: {pk}")
        # 본인 계정만 삭제 가능하도록 제한
        if request.user.pk != pk:
            raise PermissionDenied('본인의 정보만 삭제할 수 있습니다.')

        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response({"message": "Deleted successfully"}, status=200)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 프로필 수정
    def put(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)

        data = request.data.copy()

        # ✅ base64 이미지 처리 로직 추가
        image_base64 = data.get('image')
        if image_base64:
            try:
                format, imgstr = image_base64.split(';base64,')
                ext = format.split('/')[-1]
                profile.image.save(
                    f"profile_{request.user.id}.{ext}",
                    ContentFile(base64.b64decode(imgstr)),
                    save=False
                )
            except Exception as e:
                return Response({"error": f"이미지 처리 중 오류 발생: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProfileSerializer(profile, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "프로필이 수정되었습니다."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        profile.delete()
        return Response({"message": "프로필이 삭제되었습니다."}, status=status.HTTP_200_OK)
