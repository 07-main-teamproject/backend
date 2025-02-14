from django.db import models

# Create your models here.
from django.db import models
from datetime import date



class CommonModel(models.Model):
    # 생성된 시간 (고정)
    created_at = models.DateTimeField(auto_now_add=True)

    # 데이터가 업데이트된 시간 (업데이트 할 때 마다 계속 시간이 변경)
    updated_at = models.DateTimeField(auto_now=True)

    date = models.DateField(default=date.today)  # 새로 추가 → 식단 날짜 관리

    class Meta:
        abstract = True  # DB에 테이블을 추가하지 마시오.