from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Diet
from food.models import Food
from dietfood.models import DietFood
from .serializers import DietSerializer
from rest_framework.permissions import IsAuthenticated
import random
import requests
import logging

logger = logging.getLogger(__name__)  # 로깅 설정

class DietListView(APIView):
    permission_classes = [IsAuthenticated]
    # 전체 조회(만든 식단 전체 조회)
    def get(self, request):
        date = request.query_params.get("date")  # 특정 날짜 조회 기능 추가 -> 날짜에 만든 아침 점심 저녁 식단 조회가능
        if date:
            diets = Diet.objects.filter(user=request.user, date=date)
        else:
            diets = Diet.objects.filter(user=request.user)
        serializer = DietSerializer(diets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DietDetailView(APIView):
    permission_classes = [IsAuthenticated]
    # 하나의 식단 조회 예: 아침 식단
    def get(self, request, diet_id):
        """특정 식단 조회 (식단 + 포함된 음식 정보)"""
        diet = get_object_or_404(Diet,id=diet_id, user=request.user)
        serializer = DietSerializer(diet)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DietCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def fetch_food_from_external_api(self, query, max_foods=500, max_pages=10):
        """외부 API에서 검색한 음식 데이터 가져오기 (페이지네이션 적용)"""
        extracted_foods = []  # 전체 음식 데이터 저장 (초기화)
        page = 1  # 시작 페이지
        base_url = "https://world.openfoodfacts.org/cgi/search.pl"

        while len(extracted_foods) < max_foods and page <= max_pages:
            search_url = f"{base_url}?search_terms={query}&search_simple=1&action=process&json=1&page_size=150&page={page}"
            print(f"🔍 [API 요청] {search_url}", flush=True)

            try:
                response = requests.get(search_url, timeout=10)  # 타임아웃 10초
                response.raise_for_status()
                search_data = response.json()

                products = search_data.get("products", [])
                if not products:
                    print(f"📌 [페이지 {page}] 검색 결과 없음", flush=True)
                    break  # 검색 결과가 없으면 루프 종료

                #  유효한 제품 필터링 (영양 정보 포함)
                valid_products = [
                    product for product in products if "nutriments" in product and product.get("product_name")
                ]

                if not valid_products:
                    print(f"📌 [페이지 {page}] 유효한 음식 없음", flush=True)
                    break  # 더 이상 유효한 음식이 없으면 종료

                for product in valid_products:
                    if len(extracted_foods) >= max_foods:
                        break  # 최대 개수(200개)를 초과하면 종료

                    food_data = {
                        "external_id": product.get("code"),
                        "name": product.get("product_name"),
                        "calories": product.get("nutriments", {}).get("energy-kcal", 0),
                        "protein": product.get("nutriments", {}).get("proteins", 0),
                        "carbs": product.get("nutriments", {}).get("carbohydrates", 0),
                        "fat": product.get("nutriments", {}).get("fat", 0),
                        "contains_nuts": "en:nuts" in product.get("ingredients_tags", []) or
                                         "en:nuts" in product.get("categories_tags", []) or
                                         "en:nuts" in product.get("allergens_tags", []) or
                                         "en:nuts" in product.get("traces_tags", []),
                        "contains_gluten": "en:gluten" in product.get("ingredients_tags", []) or
                                           "en:gluten" in product.get("categories_tags", []) or
                                           "en:gluten" in product.get("allergens_tags", []) or
                                           "en:gluten" in product.get("traces_tags", []),
                        "contains_dairy": "en:dairy" in product.get("ingredients_tags", []) or
                                          "en:dairy" in product.get("categories_tags", []) or
                                          "en:dairy" in product.get("allergens_tags", []) or
                                          "en:dairy" in product.get("traces_tags", []),
                        "categories": product.get("categories_tags", []),
                        "tags": product.get("ingredients_tags", []),
                        "labels": product.get("labels_tags", []),
                    }
                    extracted_foods.append(food_data)

                print(f"📌 [페이지 {page}] 현재까지 수집된 음식 개수: {len(extracted_foods)}", flush=True)
                page += 1  # 다음 페이지로 이동

            except requests.exceptions.Timeout:
                print("❌ [API 요청 실패] 타임아웃 발생", flush=True)
                break  # 타임아웃 발생 시 종료

            except requests.exceptions.RequestException as e:
                print(f"❌ [API 요청 실패] {e}", flush=True)
                break  # 기타 요청 예외 발생 시 종료

        print(f"✅ [최종 데이터] 총 {len(extracted_foods)}개 음식 수집 완료", flush=True)
        return extracted_foods

    def post(self, request):
        profile = request.user.profile
        allergies = profile.allergies if profile.allergies else []
        preferences = profile.preferences if profile.preferences else []

        # 음식 선호도를 검색어로 변환 (사용자 선호도 반영)
        preference_keywords = {
            "저염식": "low-salt",
            "비건": "vegan",
            "채식": "vegetarian",
            "고단백": "high-protein"
        }

        # 기본 검색어 + 선호도 기반 검색어 설정
        selected_keywords = [preference_keywords[p] for p in preferences if p in preference_keywords]
        default_queries = ["organic", "green-dot", "nutriscore"]
        search_queries = selected_keywords if selected_keywords else default_queries

        # API 요청을 1번만 수행하여 음식 데이터 가져오기
        query = random.choice(search_queries)  # 하나의 검색어만 선택
        external_foods = self.fetch_food_from_external_api(query)  # API 한 번만 호출

        print(f"📌 [디버그] 외부 API에서 가져온 음식 개수: {len(external_foods)}", flush=True)

        # 안전한 출력 적용 (UnicodeEncodeError 방지)
        for food in external_foods[:5]:  # 샘플 5개만 출력
            try:
                print(f"📌 [디버그] 음식 데이터: {repr(food)}", flush=True)
            except UnicodeEncodeError as e:
                print(f"🚨 [경고] 인코딩 오류 발생! {e}", flush=True)

        # 중복 제거 (external_id 기준)
        unique_external_foods = {food["external_id"]: food for food in external_foods}.values()
        print(f"📌 [디버그] 중복 제거 후 음식 개수: {len(unique_external_foods)}", flush=True)

        # 알레르기 필터링 로그 추가
        print(f"📌 [디버그] 적용된 알레르기 필터: {allergies}", flush=True)

        # 필터링 적용 (알레르기 고려)
        filtered_external_foods = [
            food for food in unique_external_foods
            if not ("견과류" in allergies and food["contains_nuts"]) and
               not ("글루텐" in allergies and food["contains_gluten"]) and
               not ("유제품" in allergies and food["contains_dairy"])
        ]

        print(f"📌 [디버그] 필터링된 음식 개수: {len(filtered_external_foods)}", flush=True)
        print(f"📌 [디버그] 알레르기 필터링으로 제외된 음식 개수: {len(unique_external_foods) - len(filtered_external_foods)}",
              flush=True)

        # 최대 500개까지만 저장
        filtered_external_foods = list(filtered_external_foods)[:500]
        print(f"📌 [디버그] 최종 저장할 음식 개수 (최대 500개): {len(filtered_external_foods)}", flush=True)

        # DB 저장 전에 이미 존재하는 음식 체크
        existing_food_ids = set(Food.objects.values_list("external_id", flat=True))
        new_foods_to_save = [
            Food(**food_data) for food_data in filtered_external_foods
            if food_data["external_id"] not in existing_food_ids
        ]
        print(f"📌 [디버그] DB에 저장할 새로운 음식 개수: {len(new_foods_to_save)}", flush=True)

        # bulk_create()로 한 번에 저장 (성능 향상)
        Food.objects.bulk_create(new_foods_to_save)
        saved_foods = Food.objects.count()
        print(f"📌 [디버그] 최종 DB에 저장된 음식 개수: {saved_foods}", flush=True)

        # 기본 식단 생성 (아침, 점심, 저녁)
        default_diets = [
            {"name": "아침 식단", "user": request.user.id},
            {"name": "점심 식단", "user": request.user.id},
            {"name": "저녁 식단", "user": request.user.id}
        ]

        created_diets = []
        used_foods = set()  # 중복 방지용

        for data in default_diets:
            serializer = DietSerializer(data={"name": data["name"], "user": data["user"]})
            if serializer.is_valid():
                diet = serializer.save()
                available_foods = [food for food in Food.objects.exclude(id__in=used_foods)]  # 중복 제거

                print(f"🔍 [디버그] 최종 선택 가능한 음식 개수: {len(available_foods)}", flush=True)

                if not available_foods:
                    diet.delete()
                    return Response({"detail": "필터링된 음식이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

                # 식단에 랜덤으로 3개 음식 추가 (중복 방지)
                selected_foods = random.sample(available_foods, min(len(available_foods), 3))
                for food in selected_foods:
                    DietFood.objects.get_or_create(diet=diet, food=food, portion_size=100)
                    used_foods.add(food.id)  # 중복 방지

                created_diets.append(DietSerializer(diet).data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "기본 식단이 생성되었습니다.", "diets": created_diets}, status=status.HTTP_201_CREATED)


class DietDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, diet_id):
        """식단 삭제 (삭제된 식단 ID 포함)"""
        diet = get_object_or_404(Diet, id=diet_id, user=request.user)
        deleted_diet_id = diet.id  # 삭제 전 ID 저장
        diet.delete()  # 식단 삭제
        return Response(
            {"detail": "식단이 삭제되었습니다.", "deleted_diet_id": deleted_diet_id},
            status=status.HTTP_200_OK
        )
