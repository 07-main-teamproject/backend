from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Diet
from food.models import Food
from dietfood.models import DietFood
from .serializers import DietSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

class DietListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        diets = Diet.objects.filter(user=request.user)  # 사용자의 식단만 조회
        serializer = DietSerializer(diets, many=True)  # 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK)

class DietCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 사용자의 프로필 정보를 가져오기
        profile = request.user.profile

        # 알레르기 및 선호도 정보 가져오기
        allergies = profile.allergies
        preferences = profile.preferences

        # 기본적으로 "아침 식단", "점심 식단", "저녁 식단"을 자동으로 제공
        default_diets = [
            {"name": "아침 식단", "user": request.user.id},
            {"name": "점심 식단", "user": request.user.id},
            {"name": "저녁 식단", "user": request.user.id}
        ]

        # 선호도 및 알레르기 조건에 맞는 음식 필터링
        foods_to_include = Food.objects.all()  # 기본적으로 모든 음식

        # 선호도 필터링
        if preferences:
            for preference in preferences:
                foods_to_include = foods_to_include.filter(tags__contains=preference)

        # 알레르기 필터링
        if allergies:
            for allergy in allergies:
                if allergy == "견과류":
                    foods_to_include = foods_to_include.exclude(contains_nuts=True)
                elif allergy == "글루텐":
                    foods_to_include = foods_to_include.exclude(contains_gluten=True)
                elif allergy == "유제품":
                    foods_to_include = foods_to_include.exclude(contains_dairy=True)

        created_diets = []  # 모든 생성된 식단 정보를 저장할 리스트

        # 식단들을 저장
        for data in default_diets:
            serializer = DietSerializer(data=data)
            if serializer.is_valid():
                diet = serializer.save()

                # 기본적으로 식단에 음식 추가 (선택된 음식에서 랜덤으로 4개 추가)
                foods_for_diet = foods_to_include[:4]  # 예시: 4개의 음식을 추가
                for food in foods_for_diet:
                    DietFood.objects.create(diet=diet, food=food, portion_size=100)  # 기본적으로 100g으로 설정

                created_diets.append(serializer.data)  # 생성된 식단을 리스트에 추가

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 모든 생성된 식단 반환
        return Response({"detail": "기본 식단이 생성되었습니다.", "diets": created_diets}, status=status.HTTP_201_CREATED)

class DietUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, diet_id):
        # 식단 확인 (사용자가 만든 식단인지 확인)
        try:
            diet = Diet.objects.get(id=diet_id, user=request.user)
        except Diet.DoesNotExist:
            raise NotFound("식단을 찾을 수 없습니다.")

        # 요청된 데이터에서 음식 정보 얻기
        external_ids_to_add = request.data.get('add_foods', [])  # 외부 음식 ID 추가 요청
        external_ids_to_remove = request.data.get('remove_foods', [])  # 외부 음식 ID 제거 요청

        # 음식 추가
        for external_id in external_ids_to_add:
            try:
                food = Food.objects.get(external_id=external_id)  # external_id를 기반으로 조회
                DietFood.objects.create(diet=diet, food=food, portion_size=100)  # 기본적으로 100g으로 설정
            except Food.DoesNotExist:
                return Response({"detail": f"음식 외부 ID {external_id}를 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 음식 제거
        for external_id in external_ids_to_remove:
            try:
                diet_food = DietFood.objects.get(diet=diet, food__external_id=external_id)  # external_id를 기반으로 조회
                diet_food.delete()
            except DietFood.DoesNotExist:
                return Response({"detail": f"식단에서 해당 음식({external_id})을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 수정된 식단 정보 반환
        updated_diet = Diet.objects.get(id=diet_id, user=request.user)
        serializer = DietSerializer(updated_diet)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DietDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, diet_id):
        # 식단 확인 (사용자가 만든 식단인지 확인)
        try:
            diet = Diet.objects.get(id=diet_id, user=request.user)
            diet.delete()  # 식단 삭제
            return Response({"detail": "식단이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        except Diet.DoesNotExist:
            raise NotFound("식단을 찾을 수 없습니다.")
