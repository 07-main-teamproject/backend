from rest_framework import serializers
from .models import Food

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['id', "external_id",'name', 'calories', 'protein', 'carbs', 'fat', 'contains_nuts', 'contains_gluten', 'contains_dairy']
