from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DietFood, Diet
from food.models import Food
from .serializers import DietFoodSerializer
from rest_framework.permissions import IsAuthenticated

class DietFoodAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, diet_id):
        # diet_id로 식단을 확인
        try:
            diet = Diet.objects.get(id=diet_id, user=request.user)
        except Diet.DoesNotExist:
            return Response({"detail": "식단을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 요청에서 음식 ID와 수량을 받음
        external_id = request.data.get('external_id')  # 음식 ID
        portion_size = request.data.get('portion_size', 100)  # 기본 양 100g로 설정 (그램 단위)

        # 양이 0 이하일 경우 오류 처리
        if portion_size <= 0:
            return Response({"detail": "양은 0보다 커야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            food = Food.objects.get(external_id=external_id)
        except Food.DoesNotExist:
            return Response({"detail": "음식을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # DietFood 객체 생성
        diet_food, created = DietFood.objects.get_or_create(
            diet=diet,
            food=food,
            defaults={'portion_size': portion_size}  # 양을 portion_size로 저장
        )

        if not created:
            # 이미 식단에 음식이 존재하면 양만 업데이트
            diet_food.portion_size = portion_size
            diet_food.save()

        # 직렬화하여 응답
        serializer = DietFoodSerializer(diet_food)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class DietFoodRemoveView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, diet_id):
        # diet_id로 식단을 확인
        try:
            diet = Diet.objects.get(id=diet_id, user=request.user)
        except Diet.DoesNotExist:
            return Response({"detail": "식단을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 요청에서 음식 ID를 받음
        external_id = request.data.get('external_id')

        try:
            food = Food.objects.get(external_id=external_id)
        except Food.DoesNotExist:
            return Response({"detail": "음식을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # DietFood 객체 삭제
        try:
            diet_food = DietFood.objects.get(diet=diet, food=food)
            diet_food.delete()
            return Response({"detail": "음식이 식단에서 제거되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        except DietFood.DoesNotExist:
            return Response({"detail": "이 식단에 해당 음식이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

class DietFoodUpdatePortion_sizeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, diet_id):
        # diet_id로 식단을 확인
        try:
            diet = Diet.objects.get(id=diet_id, user=request.user)
        except Diet.DoesNotExist:
            return Response({"detail": "식단을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 요청에서 음식 ID와 수량을 받음
        external_id = request.data.get('external_id')
        portion_size = request.data.get('portion_size')

        try:
            food = Food.objects.get(external_id=external_id)
        except Food.DoesNotExist:
            return Response({"detail": "음식을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # DietFood 객체 수정
        try:
            diet_food = DietFood.objects.get(diet=diet, food=food)
            diet_food.portion_size = portion_size
            diet_food.save()
            return Response({"detail": "음식 수량을 업데이트했습니다."}, status=status.HTTP_200_OK)
        except DietFood.DoesNotExist:
            return Response({"detail": "이 식단에 해당 음식이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)



