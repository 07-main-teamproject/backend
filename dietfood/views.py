from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DietFood, Diet
from food.models import Food
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal

class DietFoodAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, diet_id):
        """음식 단일 추가 및 대량 추가 (이미 존재하면 양만 수정, 영양소 업데이트 포함)"""
        diet = get_object_or_404(Diet, id=diet_id, user=request.user)
        external_ids = request.data.get("external_ids", [])
        portion_size = request.data.get("portion_size", 100)
        merge_quantity = request.data.get("merge_quantity", False)  # 기존 양에 더하는 옵션

        if not external_ids:
            return Response({"detail": "추가할 음식 ID가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        if portion_size <= 0:
            return Response({"detail": "양은 0보다 커야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        added_foods = []

        for external_id in external_ids:
            food = Food.objects.filter(external_id=external_id).first()
            if not food:
                return Response({"detail": f"음식 ID {external_id}를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            diet_food, created = DietFood.objects.get_or_create(
                diet=diet, food=food, defaults={"portion_size": portion_size}
            )

            if not created:
                if merge_quantity:
                    diet_food.portion_size += portion_size  # 기존 양에 추가
                else:
                    diet_food.portion_size = portion_size  # 기존 양을 덮어씀

            # **영양소 업데**
            diet_food.calories = food.calories * (diet_food.portion_size / 100.0)
            diet_food.protein = food.protein * (diet_food.portion_size / 100.0)
            diet_food.carbs = food.carbs * (diet_food.portion_size / 100.0)
            diet_food.fat = food.fat * (diet_food.portion_size / 100.0)

            diet_food.save()

            added_foods.append({
                "external_id": external_id,
                "portion_size": diet_food.portion_size,
                "calories": diet_food.calories,
                "protein": diet_food.protein,
                "carbs": diet_food.carbs,
                "fat": diet_food.fat
            })

        return Response({"detail": "음식이 추가되었습니다.", "added_foods": added_foods}, status=status.HTTP_201_CREATED)


class DietFoodRemoveView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, diet_id):
        """음식 단일 삭제 및 대량 삭제"""
        diet = get_object_or_404(Diet, id=diet_id, user=request.user)
        external_ids = request.data.get("external_ids", [])

        if not external_ids:
            return Response({"detail": "삭제할 음식 ID가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        deleted_foods = []

        for external_id in external_ids:
            food = Food.objects.filter(external_id=external_id).first()
            if not food:
                return Response({"detail": f"음식 ID {external_id}를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            diet_food = DietFood.objects.filter(diet=diet, food=food).first()
            if not diet_food:
                return Response({"detail": f"이 식단에 음식 ID {external_id}가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

            diet_food.delete()
            deleted_foods.append({
                "external_id": external_id,
                "name": food.name
            })

        return Response({"detail": "음식이 삭제되었습니다.", "deleted_foods": deleted_foods}, status=status.HTTP_200_OK)


class DietFoodUpdatePortionSizeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, diet_id):
        """음식 양(포션) 수정 (대량 수정 & 개별 수정 가능, 영양소 업데이트 포함)"""
        diet = get_object_or_404(Diet, id=diet_id, user=request.user)

        # 같은 양을 여러 개의 음식에 적용
        external_ids = request.data.get("external_ids", [])
        portion_size = request.data.get("portion_size")

        # 개별적으로 다른 양을 적용
        updates = request.data.get("updates", [])

        if not external_ids and not updates:
            return Response({"detail": "수정할 음식 ID와 수량이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        updated_foods = []

        # 같은 양을 여러 개에 적용
        if external_ids and portion_size is not None:
            if portion_size <= 0:
                return Response({"detail": "양은 0보다 커야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

            for external_id in external_ids:
                food = Food.objects.filter(external_id=external_id).first()
                if not food:
                    continue  # 존재하지 않는 음식은 무시

                diet_food = DietFood.objects.filter(diet=diet, food=food).first()
                if not diet_food:
                    continue  # 해당 식단에 음식이 없으면 무시

                diet_food.portion_size = portion_size
                diet_food.calories = food.calories * (portion_size / 100)
                diet_food.protein = food.protein * (portion_size / 100)
                diet_food.carbs = food.carbs * (portion_size / 100)
                diet_food.fat = food.fat * (portion_size / 100)
                diet_food.save()

                updated_foods.append({
                    "external_id": external_id,
                    "portion_size": diet_food.portion_size
                })

        # 개별 양 적용
        for update in updates:
            external_id = update.get("external_id")
            portion_size = update.get("portion_size")

            if portion_size is None or portion_size <= 0:
                return Response({"detail": f"양은 0보다 커야 합니다. (ID: {external_id})"},
                                status=status.HTTP_400_BAD_REQUEST)

            food = Food.objects.filter(external_id=external_id).first()
            if not food:
                continue  # 존재하지 않는 음식은 무시

            diet_food = DietFood.objects.filter(diet=diet, food=food).first()
            if not diet_food:
                continue  # 해당 식단에 음식이 없으면 무시

            diet_food.portion_size = portion_size
            diet_food.calories = food.calories * (portion_size / 100)
            diet_food.protein = food.protein * (portion_size / 100)
            diet_food.carbs = food.carbs * (portion_size / 100)
            diet_food.fat = food.fat * (portion_size / 100)
            diet_food.save()

            updated_foods.append({
                "external_id": external_id,
                "portion_size": diet_food.portion_size
            })

        if not updated_foods:
            return Response({"detail": "수정된 음식이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "음식의 양이 업데이트되었습니다.", "updated_foods": updated_foods}, status=status.HTTP_200_OK)
