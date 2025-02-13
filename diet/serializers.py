from rest_framework import serializers
from .models import Diet
from dietfood.serializers import DietFoodSerializer  # DietFood 시리얼라이저 임포트


class DietSerializer(serializers.ModelSerializer):
    # 총 칼로리, 단백질, 탄수화물, 지방을 계산하기 위한 필드
    total_calories = serializers.SerializerMethodField()
    total_protein = serializers.SerializerMethodField()
    total_carbs = serializers.SerializerMethodField()
    total_fat = serializers.SerializerMethodField()

    # DietFood를 직렬화하여 해당 식단에 포함된 음식들 가져오기
    diet_foods = DietFoodSerializer(many=True, read_only=True)

    class Meta:
        model = Diet
        fields = ['id', 'user', 'name', 'image_url', 'diet_foods', 'total_calories', 'total_protein', 'total_carbs',
                  'total_fat']  # 식단에 대한 정보와 해당 식단에 포함된 음식들

    def get_total_calories(self, obj):
        # 해당 식단에 포함된 음식들의 총 칼로리 계산
        total_calories = sum(
            (diet_food.food.calories * (diet_food.portion_size / 100))  # portion_size에 비례한 칼로리 계산
            for diet_food in obj.diet_foods.all()
        )
        return total_calories

    def get_total_protein(self, obj):
        # 해당 식단에 포함된 음식들의 총 단백질 계산
        total_protein = sum(
            (diet_food.food.protein * (diet_food.portion_size / 100))  # portion_size에 비례한 단백질 계산
            for diet_food in obj.diet_foods.all()
        )
        return total_protein

    def get_total_carbs(self, obj):
        # 해당 식단에 포함된 음식들의 총 탄수화물 계산
        total_carbs = sum(
            (diet_food.food.carbs * (diet_food.portion_size / 100))  # portion_size에 비례한 탄수화물 계산
            for diet_food in obj.diet_foods.all()
        )
        return total_carbs

    def get_total_fat(self, obj):
        # 해당 식단에 포함된 음식들의 총 지방 계산
        total_fat = sum(
            (diet_food.food.fat * (diet_food.portion_size / 100))  # portion_size에 비례한 지방 계산
            for diet_food in obj.diet_foods.all()
        )
        return total_fat
