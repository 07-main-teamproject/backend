from rest_framework import serializers
from .models import DietFood
from food.serializers import FoodSerializer  # Food 시리얼라이저 임포트

class DietFoodSerializer(serializers.ModelSerializer):
    food = FoodSerializer()  # food를 포함하여 상세 정보도 직렬화

    class Meta:
        model = DietFood
        fields = ['diet', 'food', 'portion_size']  # 음식, 식단, 양
