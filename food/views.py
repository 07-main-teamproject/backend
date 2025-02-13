from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from food.models import Food
import requests
from django.core.cache import cache

class FoodInfoView(APIView):
    def get(self, request):
        query = request.query_params.get("query")  # 사용자가 입력한 query를 가져옴 예:?query=banana
        # 검색어가 없을 경우 에러 반환
        if not query:
            return Response({"detail": "음식 이름을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 캐시에서 데이터 확인
        cache_key = f"food_info_{query}"  # 검색어를 이용해 캐시 키 생성 (food_info_banana)
        cached_data = cache.get(cache_key)  # 이미 캐시에 저장된 데이터가 있으면 가져옴
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)  # 캐싱된 데이터 반환

        # DB에서 해당 음식이 존재하는지 확인
        food_in_db = Food.objects.filter(name__icontains=query).first()  # 이름으로 검색 (부분 일치)
        if food_in_db:
            # DB에 저장된 음식이 있다면, DB에서 가져온 데이터를 응답으로 반환
            food_data = {
                "external_id": food_in_db.external_id,
                "name": food_in_db.name,
                "calories": food_in_db.calories,
                "protein": food_in_db.protein,
                "carbs": food_in_db.carbs,
                "fat": food_in_db.fat,
                "contains_nuts": food_in_db.contains_nuts,
                "contains_gluten": food_in_db.contains_gluten,
                "contains_dairy": food_in_db.contains_dairy,
                "categories": food_in_db.categories,  # 카테고리 태그 추가
                "tags": food_in_db.tags,  # 성분 태그 추가
                "labels": food_in_db.labels  #  라벨 데이터 포함
            }
            return Response(food_data, status=status.HTTP_200_OK)

        # 캐시와 DB에서 찾지 못했으면 외부 API 호출
        search_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1"
        try:
            search_response = requests.get(search_url, timeout=50)  # 타임아웃 설정 (시간 초과 방지)
            search_response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
            search_data = search_response.json()  # 정상적으로 가져오면 search_data에 저장됨
        except requests.exceptions.Timeout:
            return Response({"detail": "외부 API 응답이 너무 느립니다."}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.exceptions.RequestException:
            return Response({"detail": "외부 API 요청 실패"}, status=status.HTTP_502_BAD_GATEWAY)

        # API 응답 데이터에서 음식 정보 추출
        if search_response.status_code == 200:
            products = search_data.get("products", [])  # api 응답에서 products 리스트를 가져옴

            if products:
                product = products[0]  # 첫 번째 음식만 선택 (첫 번째 음식은 검색어와 가장 관련이 높은 음식일 가능성이 높음)
                # 음식 정보 생성 (기존 모델에 맞춰 저장)
                food_data = {
                    "external_id": product.get("code", None),
                    "name": product.get("product_name", query),
                    "calories": product.get("nutriments", {}).get("energy-kcal", 0),
                    "protein": product.get("nutriments", {}).get("proteins", 0),
                    "carbs": product.get("nutriments", {}).get("carbohydrates", 0),
                    "fat": product.get("nutriments", {}).get("fat", 0),
                    "contains_nuts": "en:nuts" in product.get("ingredients_tags", []) or "en:nuts" in product.get("categories_tags", []) or "en:nuts" in product.get("allergens_tags", []) or "en:nuts" in product.get("traces_tags", []),
                    "contains_gluten": "en:gluten" in product.get("ingredients_tags", []) or "en:gluten" in product.get("categories_tags", []) or "en:gluten" in product.get("allergens_tags", []) or "en:gluten" in product.get("traces_tags", []),
                    "contains_dairy": "en:dairy" in product.get("ingredients_tags", []) or "en:dairy" in product.get("categories_tags", []) or "en:dairy" in product.get("allergens_tags", []) or "en:dairy" in product.get("traces_tags", []),
                    "categories": product.get("categories_tags", []),  # 카테고리 태그
                    "tags": product.get("ingredients_tags", []),      # 성분 태그
                    "labels": product.get("labels_tags", [])  #  라벨 데이터 추가
                }

                # 외부에서 가져온 데이터를 DB에 저장 (새로운 음식 객체로 생성)
                new_food = Food.objects.create(
                    external_id=food_data["external_id"],
                    name=food_data["name"],
                    calories=food_data["calories"],
                    protein=food_data["protein"],
                    carbs=food_data["carbs"],
                    fat=food_data["fat"],
                    contains_nuts=food_data["contains_nuts"],
                    contains_gluten=food_data["contains_gluten"],
                    contains_dairy=food_data["contains_dairy"],
                    tags=food_data["tags"],
                    categories=food_data["categories"],
                    labels=food_data["labels"]  #  라벨 저장
                )

                return Response(food_data, status=status.HTTP_200_OK)

        return Response({"detail": "검색된 음식을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
