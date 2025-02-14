from rest_framework import serializers

from dietfood.models import DietFood
from .models import Diet
from dietfood.serializers import DietFoodSerializer  # DietFood 시리얼라이저 임포트


class DietSerializer(serializers.ModelSerializer):
    # 총 칼로리, 단백질, 탄수화물, 지방을 계산하기 위한 필드
    total_calories = serializers.SerializerMethodField()
    total_protein = serializers.SerializerMethodField()
    total_carbs = serializers.SerializerMethodField()
    total_fat = serializers.SerializerMethodField()
    diet_foods = serializers.SerializerMethodField()
    # DietFood를 직렬화하여 해당 식단에 포함된 음식들 가져오기
    # diet_foods = DietFoodSerializer(many=True, read_only=True)

    class Meta:
        model = Diet
        fields = ['id', 'user', 'name', 'image_url', "date", 'diet_foods', 'total_calories', 'total_protein', 'total_carbs',
                  'total_fat']  # 식단에 대한 정보와 해당 식단에 포함된 음식들

    def get_diet_foods(self, obj):
        """ 해당 식단의 DietFood 목록을 가져옴 """
        diet_foods = DietFood.objects.filter(diet=obj)
        return DietFoodSerializer(diet_foods, many=True).data

    def get_total_calories(self, obj):
        total_calories = sum(
            (float(diet_food.food.calories) * (float(diet_food.portion_size) / 100))
            for diet_food in obj.diet_foods.all()
        )
        return total_calories

    def get_total_protein(self, obj):
        total_protein = sum(
            (float(diet_food.food.protein) * (float(diet_food.portion_size) / 100))
            for diet_food in obj.diet_foods.all()
        )
        return total_protein

    def get_total_carbs(self, obj):
        total_carbs = sum(
            (float(diet_food.food.carbs) * (float(diet_food.portion_size) / 100))
            for diet_food in obj.diet_foods.all()
        )
        return total_carbs

    def get_total_fat(self, obj):
        total_fat = sum(
            (float(diet_food.food.fat) * (float(diet_food.portion_size) / 100))
            for diet_food in obj.diet_foods.all()
        )
        return total_fat
