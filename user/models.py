from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from common.models import CommonModel

# ✅ 사용자 정의 매니저
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # 비밀번호 해싱(암호화)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("슈퍼유저는 is_staff=True여야 합니다.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("슈퍼유저는 is_superuser=True여야 합니다.")

        return self.create_user(email, password, **extra_fields)


# ✅ `User` 모델 정의 (이메일을 ID로 사용)
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)  # 이메일 = ID
    name = models.CharField(max_length=50)
    nickname = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)  # 비밀번호는 암호화되므로 길이 조정
    last_login = models.DateTimeField(auto_now=True)  # 마지막 로그인 기록
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()  # ✅ 사용자 정의 매니저 적용

    USERNAME_FIELD = 'email'  # ✅ 이메일을 로그인 ID로 사용
    REQUIRED_FIELDS = ['name']  # 슈퍼유저 생성 시 추가 필수 필드

    class Meta:
        db_table = 'users'  # 데이터베이스 테이블 이름 설정

    def __str__(self):
        return self.email

# ✅ Profile 모델 추가
class Profile(CommonModel):  # ✅ CommonModel을 상속받아 생성/수정 시간 자동 추가
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    target_weight = models.FloatField(null=True, blank=True)
    allergies = models.TextField(blank=True, null=True)  # ✅ 알레르기 정보 (선택 사항)
    preferences = models.TextField(blank=True, null=True)  # ✅ 음식 선호도

    def __str__(self):
        return f"{self.user.email}의 프로필"