from django.db import models
from common.models import CommonModel
from django.conf import settings

class Diet(CommonModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="diets")
    name = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)

    def get_foods(self):
        return self.diet_foods.all()  # 해당 식단에 포함된 모든 음식 가져오기

    def __str__(self):
        return self.name
