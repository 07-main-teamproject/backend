from rest_framework import serializers
from .models import User,Profile
from django.contrib.auth.hashers import check_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "name", "nickname"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value

    def validate_nickname(self, value):
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            name=validated_data["name"],
            nickname=validated_data.get("nickname", "anonymous"),
        )
        user.set_password(validated_data["password"])
        user.save()

        # ✅ 회원가입 시 자동으로 Profile 생성
        Profile.objects.create(user=user)

        return user


# ✅ 로그인 Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])  # 이메일로 사용자 검색
        except User.DoesNotExist:
            raise serializers.ValidationError("이메일 또는 비밀번호가 잘못되었습니다.")

        if not check_password(data['password'], user.password):  # 비밀번호 검증
            raise serializers.ValidationError("이메일 또는 비밀번호가 잘못되었습니다.")

        return user  # 검증된 사용자 반환





# ✅ 회원 정보 Serializer (Profile 정보 포함)
class UserSerializer(serializers.ModelSerializer):
    #profile = ProfileSerializer(read_only=True)  # ✅ User 조회 시 Profile 정보도 포함

    class Meta:
        model = User
        fields = ["id", "email", "name", "nickname", "is_staff", "is_active"]  # ✅ Profile 추가


# ✅ 회원 정보 수정 Serializer
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "nickname"]