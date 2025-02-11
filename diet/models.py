from django.db import models
from common.models import CommonModel
from django.conf import settings

class Diet(CommonModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 사용자가 만든 식단 'user' 모델과 연결 (1명의 사용자는 여러개의 식단을 가질 수 있음)
    name = models.CharField(max_length=255) # 식단 이름 ("아침 식단", "점심 식단", "저녁 식단")
    image_url = models.URLField(blank=True, null=True) # 식단 이미지 url (선택 사항, 없을 수도 있음)

    def __str__(self):
        # 해당 식단에 속한 DietFood 가져오기
        foods = self.diet_foods.all()  # related_name="diet_foods"로 연결된 모든 음식 가져옴
        food_list = [f"{food.name}({food.quantity}{food.unit})" for food in foods]  # 음식명 + 양 + 단위
        food_str = ", ".join(food_list)  # 쉼표로 구분해서 나열

        return f"{self.user.nickname}의 {self.name} - {food_str}"  # "홍길동의 점심 식단 - 음식1, 음식2, 음식3"