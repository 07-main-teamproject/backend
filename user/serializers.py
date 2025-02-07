from rest_framework import serializers
from .models import User, Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'nickname']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # 사용자 정보 포함

    class Meta:
        model = Profile
        fields = '__all__'
