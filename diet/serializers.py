from rest_framework import serializers
from .models import Diet

class DietSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diet # Diet 모델을 기반으로 Serializers 생성
        fields = ["id","user","name","image_url",'created_at', 'updated_at'] # JSON으로 반환할 필드 지정
