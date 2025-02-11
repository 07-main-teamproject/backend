from django.db import models
from common.models import CommonModel

class DietFood(CommonModel):
    diet = models.ForeignKey("diet.Diet", on_delete=models.CASCADE) # Diet 모델과 연결 ,DB에는 diet_id 컬럼으로 저장됨
    external_food_id = models.CharField(max_length=255) # 외부 API에서 가져온 음식 ID
    name = models.CharField(max_length=255)  # 음식 이름
    calories = models.FloatField()  # 칼로리
    protein = models.FloatField()  # 단백질
    carbs = models.FloatField()  # 탄수화물
    fat = models.FloatField()  # 지방
    # 100g 기준 영양소 값을 자동으로 계산
    quantity = models.FloatField(default=100)  # ✅ 음식의 양 (기본값 100g)
    unit = models.CharField(max_length=10, default="g")  # ✅ 단위 (g, ml, 개 등)
    # 알레르기 포함 여부
    contains_nuts = models.BooleanField(default=False)  # 견과류 포함 여부
    contains_gluten = models.BooleanField(default=False)  # 글루텐 포함 여부
    contains_dairy = models.BooleanField(default=False)  # 유제품 포함 여부

