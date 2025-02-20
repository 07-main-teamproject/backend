import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import User, Profile
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
            nickname=validated_data.get("nickname"),
        )
        user.set_password(validated_data["password"])
        user.save()

        # ✅ 회원가입 시 자동으로 Profile 생성
        Profile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("이메일이 잘못되었습니다.")

        if not check_password(data['password'], user.password):
            raise serializers.ValidationError("비밀번호가 잘못되었습니다.")

        return user


class ProfileSerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False)  # Base64 받을 수 있게 허용
    gender = serializers.CharField()
    class Meta:
        model = Profile
        fields = ["age", "gender", "height", "weight", "target_weight", "allergies", "preferences", "image"]

    # ✅ 성별 변환 로직 추가
    def validate_gender(self, value):
        gender_map = {"남성": "M", "여성": "F", "기타": "O", "M": "M", "F": "F", "O": "O"}
        if value not in gender_map:
            raise serializers.ValidationError("성별은 '남성', '여성', '기타', 'M', 'F', 'O' 중 하나여야 합니다.")
        return gender_map[value]

    # ✅ 알레르기 유효성 검사
    def validate_allergies(self, value):
        VALID_ALLERGIES = Profile.VALID_ALLERGIES
        if not isinstance(value, list):
            raise serializers.ValidationError("알레르기는 리스트 형태여야 합니다.")
        invalid_values = [item for item in value if item not in VALID_ALLERGIES]
        if invalid_values:
            raise serializers.ValidationError(f"유효하지 않은 알레르기 값: {invalid_values}")
        return value

    # ✅ 음식 선호도 유효성 검사
    def validate_preferences(self, value):
        VALID_PREFERENCES = Profile.VALID_PREFERENCES
        if not isinstance(value, list):
            raise serializers.ValidationError("음식 선호도는 리스트 형태여야 합니다.")
        invalid_values = [item for item in value if item not in VALID_PREFERENCES]
        if invalid_values:
            raise serializers.ValidationError(f"유효하지 않은 음식 선호도 값: {invalid_values}")
        return value

    # ✅ update 메서드에서 Base64 이미지 처리 로직 추가
    def update(self, instance, validated_data):
        image_data = validated_data.pop('image', None)

        if image_data:
            try:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                instance.image.save(
                    f"profile_{instance.user.id}.{ext}",
                    ContentFile(base64.b64decode(imgstr)),
                    save=False
                )
            except Exception as e:
                raise serializers.ValidationError(f"이미지 처리 중 오류 발생: {str(e)}")

        return super().update(instance, validated_data)

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "name", "nickname", "profile"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "nickname"]
