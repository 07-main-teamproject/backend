from rest_framework import serializers
from .models import DietFood

class DietFoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietFood
        fields = [
            "id", "diet", "external_food_id", "name", "calories",
            "protein", "carbs", "fat", "quantity", "unit", "contains_nuts",
            "contains_gluten", "contains_dairy", "created_at" , "updated_at"
        ]  #  JSON 응답에 포함할 필드 지정
