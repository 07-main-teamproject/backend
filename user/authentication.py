# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework_simplejwt.settings import api_settings
# from user.models import User  # ✅ User 모델 직접 가져오기
#
# class CookieJWTAuthentication(JWTAuthentication):
#     def authenticate(self, request):
#         # ✅ 쿠키에서 access_token 가져오기
#         access_token = request.COOKIES.get("access_token")
#         if not access_token:
#             return None  # 인증 실패 (쿠키에 토큰 없음)
#
#         try:
#             # ✅ 토큰 유효성 검증
#             validated_token = self.get_validated_token(access_token)
#         except Exception:
#             return None  # 유효하지 않은 토큰
#
#         try:
#             # ✅ 토큰에서 user_id 추출 후 사용자 조회
#             user_id = validated_token[api_settings.USER_ID_CLAIM]
#             user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
#         except User.DoesNotExist:
#             return None  # 유효하지 않은 사용자 ID
#         except Exception:
#             return None  # 기타 예외
#
#         return user, validated_token
