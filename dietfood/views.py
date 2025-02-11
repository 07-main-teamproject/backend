from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from  rest_framework import status
from django.shortcuts import get_object_or_404
from .models import DietFood
from diet.models import Diet
from .serializers import DietFoodSerializer
import requests

class DietFoodView(APIView):
    permission_classes = [IsAuthenticated] # 로그인한 사용자만 API를 사용 할 수 있도록 설정

    """ 특정 식단에 음식 추가 API"""
    def post(self, request):
        diet_id = request.data.get('diet_id') # 요청 데이터에서 'diet_id' 값을 가져옴 (어떤 식단에 추가할지)
        external_food_id = request.data.get('external_food_id') # 요청 데이터에서 'external_food_id' 값을 가져옴 (외부 API의 음식 ID)
        quantity = float(request.data.get('quantity' ,100)) # 요청 데이터에서 'quantity' 값을 가져오고 없으면 기본값 100g
        unit = request.data.get('unit','g') # 요청 데이터에서 'unit' 값을 가져오고 없으면 기본값 'g' 설정

        # 사용자가 diet_id 또는 external_food_id 입력하지 않았다면 에러 메시지 반환
        if not diet_id or not external_food_id:
            return  Response({"error": "diet_id와 external_food_id를 입력하세요"}, status=status.HTTP_400_BAD_REQUEST)

        diet = get_object_or_404(Diet, id=diet_id, user=request.user) # 사용자의 특정 식단을 가져오거나 없으면 404 오류 반환

        food_url = f"https://world.openfoodfacts.org/api/v0/product/{external_food_id}.json"  # OpenFoodFacts API에서 음식 정보를 가져올 URL 생성
        response = requests.get(food_url, timeout=20)  # 외부 API에 GET 요청을 보내고, 타임아웃(최대 20초)을 설정

        if response.status_code != 200: # API 요청 실패하면
            return Response({"error": "음식 정보를 가져올 수 없습니다."}, status=status.HTTP_502_BAD_GATEWAY) # 에러 반환

        food_data = response.json().get('products', {}) # API 응답을 JSON 형식으로 변환하고 'product' 키의 데이터를 가져옴, 데이터가 없으면 {}(빈 딕셔너리)로 기본값 설정
        name = food_data.get("product_name", "알 수 없는 음식")  # 음식 이름 가져오기 (없으면 기본값 "알 수 없는 음식")
        calories = food_data.get("nutriments", {}).get("energy-kcal", 0)  # 칼로리 정보 (없으면 기본값 0)

        diet_food = DietFood.objects.create(
            diet=diet,
            external_food_id=external_food_id,
            name=name,
            calories=(calories * (quantity / 100)),  #  100g 기준 → 입력한 양 기준으로 칼로리 계산
            quantity=quantity,
            unit=unit
        )

        return Response(DietFoodSerializer(diet_food).data, status=status.HTTP_201_CREATED) # 생성된 데이터를 JSON으로 변환하여 응답 반환

    """ 특정 식단의 음식 목록 조회 API """
    def get(self, request):
        diet_id = request.query_params.get("diet_id")  # 요청에서 diet_id 가져오기

        # diet_id가 없으면 "diet_id를 입력하세요." 에러 메시지 반환.
        if not diet_id:
            return Response({"error": "diet_id를 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        diet = get_object_or_404(Diet, id=diet_id, user=request.user)  # 현재 사용자의 식단인지 확인
        diet_foods = DietFood.objects.filter(diet=diet)  # 해당 식단에 포함된 모든 음식 조회

        return Response(DietFoodSerializer(diet_foods, many=True).data, status=status.HTTP_200_OK)  # 조회된 데이터를 JSON으로 변환하여 응답 반환

    """ 특정 식단에서 음식 삭제 API """
    def delete(self, request):
        # 삭제할 식단 ID와 음식 ID를 URL에서 가져옴.
        diet_id = request.query_params.get("diet_id")
        external_food_id = request.query_params.get("external_food_id")

        # diet_id 또는 external_food_id가 없을 경우, 에러 메시지를 반환
        if not diet_id or not external_food_id:
            return Response({"error": "diet_id와 external_food_id를 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 해당 음식이 존재하는지 확인하고 삭제
        diet_food = get_object_or_404(DietFood, diet_id=diet_id, external_food_id=external_food_id,diet__user=request.user)
        diet_food.delete()

        return Response({"message": "음식이 삭제되었습니다."}, status=status.HTTP_200_OK) # 성공적으로 삭제되었다는 응답 반환.






