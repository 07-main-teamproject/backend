from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from .models import Diet
from dietfood.models import DietFood
from .serializers import DietSerializer
from dietfood.serializers import DietFoodSerializer
class DietView(APIView):
    permission_classes = [IsAuthenticated] # 로그인한 사용자만 접근 가능

    """ 식단 API (자동 설정 + 직접 선택) """
    def post(self, request):
        user = request.user # 현재 요청을 보낸 사용자
        input_name = request.data.get('name') # 사용자가 입력한 식단 이름 (없으면 자동 설정)

        existing_diets = Diet.objects.filter(user=user).count() # 사용자의 기존 식단 개수를 확인해 기본 이름을 자동 설정할 때 사용

        # 기본 식단 이름 추천 (자동 설정), 3개 이상 식단을 만들었다면 추가 식단1,2 처럼 이름을 설정
        meal_names = ["아침 식단", "점심 식단", "저녁 식단"]
        default_name = meal_names[existing_diets] if existing_diets < 3 else f"추가 식단 {existing_diets - 2}"


        diet_name = input_name if input_name else default_name # 사용자가 입력한 값이 있으면 input_name 없으면 자동 설정된 default_name사용


        diet = Diet.objects.create(user=user, name=diet_name) # 새로운 식단 생성 DB에 저장됨

        return Response({"message": f"새로운 '{diet_name}'이 생성되었습니다.", "diet_id": diet.id}, status=status.HTTP_201_CREATED) # 성공적으로 식단이 생성되었음을 응답

    """ 전체 식단 목록 조회 & 특정 식단 상세 조회 API """
    def get(self, request):
        diet_id = request.query_params.get("diet_id")  # URL에서 사용자가 조회하려는`diet_id`를 가져옴

        if diet_id:  # 사용자가 특정 diet_id를 조회하는 경우 실행
            cache_key = f"diet_info_{diet_id}"  # 캐시 키를 diet_info_1처럼 생성
            cached_data = cache.get(cache_key)  # 이전에 조회한 데이터가 캐시에 저장되어 있다면 가져옴
            if cached_data:
                return Response(cached_data, status=status.HTTP_200_OK) # 캐쉬 데이터 반환

            diet = get_object_or_404(Diet, id=diet_id, user=request.user) # DB에서 조회 + 404 자동 처리 (캐시에 없을 경우)

            # 해당 식단의 모든 음식 가져와서 총 영양소 계산
            foods = DietFood.objects.filter(diet=diet)
            total_calories = sum(food.calories for food in foods) # 모든 음식의 칼로리를 더함
            total_protein = sum(food.protein for food in foods)   # 모든 음식의 단백지를 더함
            total_carbs = sum(food.carbs for food in foods)       # 모든 음식의 탄수화물을 더함
            total_fat = sum(food.fat for food in foods)           # 모든 음식의 지방을 더함

            # 응답 데이터 구성
            response_data = {
                "diet_id": diet.id,    # 식단의 고유 id
                "name": diet.name,     # 식단 이름 (예:아침 식단)
                "total_calories": total_calories, # 계산된 총 칼로리
                "total_protein": total_protein,   # 계산된 총 단백질
                "total_carbs": total_carbs,       # 계산된 총 탄수화물
                "total_fat": total_fat,           # 계산된 총 지방
                "image_url": diet.image_url,      # 식단의 이미지 (없으면 null)
                "foods": DietFoodSerializer(foods, many=True).data  # 이 식단에 포함된 음식 목록
            }


            cache.set(cache_key, response_data, timeout=3600)  # 캐시에 저장 (60분 동안 유지), DB를 거치지 않고 빠르게 응답

            return Response(response_data, status=status.HTTP_200_OK)  # 특정 식단 정보를 정상적으로 반환

            # 전체 식단 목록 조회 (diet_id 없이 요청한 경우)
        diets = Diet.objects.filter(user=request.user).order_by("-created_at")  # 현재 사용자가 가지고 있는 모든 식단을 최신순으로 정렬
        return Response(DietSerializer(diets, many=True).data, status=status.HTTP_200_OK) # 사용자의 모든 식단을 반환

    """ 특정 식단 이름 수정 API """
    def patch(self, request):
        # 사용자가 수정학 식단 id와 새로운 식단 이름을 요청에서 가져옴
        diet_id = request.query_params.get("diet_id")
        new_name = request.data.get("name")

        # diet_id 또는 name이 없을 경우 에러 반환
        if not diet_id or not new_name:
            return Response({"error": "diet_id와 name을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        diet = get_object_or_404(Diet, id=diet_id, user=request.user) # DB에서 해당 diet_id와 user가 일치하는 식단을 가져옴, 데이터가 없으면 자동으로 404응답 반환
        diet.name = new_name  # 식단의 name 값을 새로운 값으로 변경
        diet.save()           # 변경된 데이터를 DB에 저장
        cache.delete(f"diet_info_{diet_id}") # 캐시 삭제 (최신 데이터 유지)

        return Response({"message": "식단 이름이 수정되었습니다.", "diet_id": diet.id, "new_name": diet.name}, status=status.HTTP_200_OK) # 성공 메시지와 수정된 식단id, 변경된 식단 이름 반환

    """ 특정 식단 삭제 API """
    def delete(self, request):
        diet_id = request.query_params.get("diet_id") # 삭제하려는 diet_id 가져옴

        # diet_id가 없을 경우 에러 반환
        if not diet_id:
            return Response({"error": "diet_id를 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        diet = get_object_or_404(Diet, id=diet_id, user=request.user) # DB에서 해당 diet_id와 user가 일치하는 식단을 가져옴, 데이터가 없으면 자동으로 404응답 반환
        diet.delete() # 해당 식단 DB에서 삭제
        cache.delete(f"diet_info_{diet_id}") # 캐시 삭제 (최신 데이터 유지)

        return Response({"message": "식단이 삭제되었습니다.", "diet_id": diet_id}, status=status.HTTP_200_OK) # 성공 메시지와 삭제된 식단 id반환







