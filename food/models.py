from django.db import models
from common.models import CommonModel

class Food(CommonModel):
    external_id = models.CharField(max_length=255, unique=True)  # 외부 API의 id를 이 필드에 저장
    name = models.CharField(max_length=255)
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    contains_nuts = models.BooleanField(default=False)
    contains_gluten = models.BooleanField(default=False)
    contains_dairy = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True, null=True)
    labels = models.JSONField(default=list, blank=True, null=True)


    def __str__(self):
        return self.name  # 음식 이름이 출력되도록 설정