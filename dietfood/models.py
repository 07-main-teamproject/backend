from django.db import models
from common.models import CommonModel
from diet.models import Diet  # Diet 모델을 임포트
from food.models import Food  # Food 모델을 임포트

class DietFood(CommonModel):
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE, related_name="diet_foods")  # Diet와 연결
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="food_diets",default=1)  # Food와 연결
    portion_size = models.DecimalField(max_digits=6, decimal_places=2,default=100)  # 음식의 양 (예: 200g, 1개 등)

    class Meta:
        unique_together = ('diet', 'food')  # 같은 식단에 동일한 음식을 두 번 추가하지 않도록 설정

    def __str__(self):
        return f"{self.diet.name} - {self.food.name} ({self.portion_size}g)"
