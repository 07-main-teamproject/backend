from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Diet
from food.models import Food
from dietfood.models import DietFood
from .serializers import DietSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
import random
import requests
from django.core.cache import cache

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

    def fetch_food_from_external_api(self, query):
        """외부 API에서 검색한 음식 데이터 가져오기 (캐싱 적용)"""
        cache_key = f"food_search_{query.replace(' ', '_')}"

        cached_data = cache.get(cache_key)
        if cached_data:
            print(f"[캐시 사용] {query} 검색 결과 반환")
            return cached_data

        search_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1"
        print(f"🔍 [API 요청] {search_url}")

        try:
            response = requests.get(search_url, timeout=10)  # ⏳ 타임아웃을 10초로 늘림
            response.raise_for_status()
            search_data = response.json()

            products = search_data.get("products", [])
            if not products:
                print("[API 응답] 검색 결과 없음")
                return []

            #  유효한 제품 필터링 (영양 정보 포함)
            valid_products = [
                product for product in products if "nutriments" in product and product.get("product_name")
            ]

            if not valid_products:
                print("[API 응답] 유효한 음식 없음")
                return []

            extracted_foods = []
            for product in valid_products[:5]:  # 최대 5개까지만 가져오기
                food_data = {
                    "external_id": product.get("code"),
                    "name": product.get("product_name"),
                    "calories": product.get("nutriments", {}).get("energy-kcal", 0),
                    "protein": product.get("nutriments", {}).get("proteins", 0),
                    "carbs": product.get("nutriments", {}).get("carbohydrates", 0),
                    "fat": product.get("nutriments", {}).get("fat", 0),
                    "contains_nuts": "en:nuts" in product.get("ingredients_tags", []),
                    "contains_gluten": "en:gluten" in product.get("ingredients_tags", []),
                    "contains_dairy": "en:dairy" in product.get("ingredients_tags", []),
                    "labels": product.get("labels_tags", []),
                }
                extracted_foods.append(food_data)

            print(f" [추출된 음식 데이터] {extracted_foods}")

            #  캐싱
            cache.set(cache_key, extracted_foods, timeout=600)

            return extracted_foods

        except requests.exceptions.Timeout:
            print(" [API 요청 실패] 타임아웃 발생")
            return []  # 응답이 없으면 빈 리스트 반환

        except requests.exceptions.RequestException as e:
            print(f" [API 요청 실패] {e}")
            return []

    def post(self, request):
        profile = request.user.profile
        allergies = profile.allergies if profile.allergies else []
        preferences = profile.preferences if profile.preferences else []

        # 선호도에 맞는 검색어 설정
        preference_keywords = {
            "Low salt": "low salt",
            "Vegan": "vegan",
            "Vegetarian": "vegetarian",
            "High proteins": "high protein"
        }

        # 기본 검색어 + 선호도 기반 검색어 설정
        selected_keywords = [preference_keywords[p] for p in preferences if p in preference_keywords]
        default_queries = ["Organic", "Green Dot", "Nutriscore"]
        search_queries = selected_keywords if selected_keywords else default_queries

        default_diets = [
            {"name": "아침 식단", "user": request.user.id, "query": random.choice(search_queries)},
            {"name": "점심 식단", "user": request.user.id, "query": random.choice(search_queries)},
            {"name": "저녁 식단", "user": request.user.id, "query": random.choice(search_queries)}
        ]

        # DB에서 필터링하여 음식 가져오기
        all_foods = list(Food.objects.all())

        if "견과류" in allergies:
            all_foods = [food for food in all_foods if not food.contains_nuts]
        if "글루텐" in allergies:
            all_foods = [food for food in all_foods if not food.contains_gluten]
        if "유제품" in allergies:
            all_foods = [food for food in all_foods if not food.contains_dairy]

        created_diets = []
        used_foods = set()  # 사용된 음식 저장 (중복 방지)

        for data in default_diets:
            serializer = DietSerializer(data={"name": data["name"], "user": data["user"]})
            if serializer.is_valid():
                diet = serializer.save()
                available_foods = [food for food in all_foods if food.id not in used_foods]

                print(f"🔍 [디버그] 초기 선택된 음식 개수: {len(available_foods)}")

                # 부족한 음식 개수 확인 (한 식단에 3개만 포함)
                remaining_count = 3 - len(available_foods)

                # 부족하면 API에서 추가 음식 가져오기
                if remaining_count > 0:
                    query = data["query"]  # 선호도 기반 검색어 적용
                    print(f"🔍 [API 요청] {query} 키워드로 음식 검색")

                    external_foods = self.fetch_food_from_external_api(query)

                    print(f"🔍 [디버그] 외부 API에서 가져온 음식 개수: {len(external_foods)}")

                    #  외부 API에서도 필터링 적용 (알레르기 제외)
                    filtered_external_foods = [
                        food for food in external_foods
                        if not ("견과류" in allergies and food["contains_nuts"]) and
                           not ("글루텐" in allergies and food["contains_gluten"]) and
                           not ("유제품" in allergies and food["contains_dairy"])
                    ]

                    print(f"🔍 [디버그] 필터링 후 남은 음식 개수: {len(filtered_external_foods)}")

                    if filtered_external_foods:
                        new_foods = random.sample(filtered_external_foods,
                                                  min(len(filtered_external_foods), remaining_count))
                        for food_data in new_foods:
                            try:
                                print(f"[DB 저장 시도] {food_data}")
                                new_food, created = Food.objects.get_or_create(
                                    external_id=food_data["external_id"],
                                    defaults=food_data
                                )

                                available_foods.append(new_food)
                                if created:
                                    print(f"[DB 저장 성공] 음식 추가됨: {new_food.name}")
                                else:
                                    print(f"[DB 존재] 기존 음식 추가됨: {new_food.name}")

                            except Exception as e:
                                print(f"❌ [DB 저장 중 오류 발생] {e}")

                print(f"🔍 [디버그] 최종 식단에 포함된 음식 개수: {len(available_foods)}")

                if not available_foods:
                    diet.delete()
                    return Response(
                        {"detail": "필터링된 음식이 없습니다. 음식 선호도 또는 알레르기 설정을 확인하세요."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                selected_foods = random.sample(available_foods, min(len(available_foods), 3))  # 각 식단에 랜덤 음식 추가
                for food in selected_foods:
                    DietFood.objects.create(diet=diet, food=food, portion_size=100)
                    used_foods.add(food.id)  # 중복 방지용으로 사용된 음식 저장

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
