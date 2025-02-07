from rest_framework import serializers
from .models import Food

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = "__all__"  # 모든 필드를 자동 변환