from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
import requests


class FoodInfoView(APIView):
    def get(self, request):
        query = request.query_params.get("query")
        if not query:
            return Response({"error": "음식 이름을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 캐시에서 데이터 확인 (캐시 키 = 검색어)
        cache_key = f"food_info_{query}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)  # 캐싱된 데이터 반환

        # 캐시에 없으면 OpenFoodFacts 검색 API 호출
        search_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1"
        try:
            search_response = requests.get(search_url, timeout=20)  # 타임아웃  설정
            search_response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
            search_data = search_response.json()
        except requests.exceptions.Timeout:
            return Response({"error": "외부 API 응답이 너무 느립니다."}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.exceptions.RequestException:
            return Response({"error": "외부 API 요청 실패"}, status=status.HTTP_502_BAD_GATEWAY)

        if search_response.status_code == 200:
            search_data = search_response.json()
            products = search_data.get("products", [])

            if products:
                food_list = []

                # 최대 3개의 유사한 음식 반환
                for product in products[:3]:
                    food_data = {
                        "id": product.get("code", None),
                        "name": product.get("product_name", query),
                        "calories": product.get("nutriments", {}).get("energy-kcal", 0),
                        "protein": product.get("nutriments", {}).get("proteins", 0),
                        "carbs": product.get("nutriments", {}).get("carbohydrates", 0),
                        "fat": product.get("nutriments", {}).get("fat", 0),

                        # `nuts`, `gluten`, `dairy` 포함 여부 확인
                        "contains_nuts": "en:nuts" in product.get("ingredients_tags", []) or "en:nuts" in product.get("categories_tags", []) or "en:nuts" in product.get("allergens_tags", []) or "en:nuts" in product.get("traces_tags", []),
                        "contains_gluten": "en:gluten" in product.get("ingredients_tags",[]) or "en:gluten" in product.get("categories_tags", []) or "en:gluten" in product.get("allergens_tags",[]) or "en:gluten" in product.get("traces_tags", []),
                        "contains_dairy": "en:dairy" in product.get("ingredients_tags",[]) or "en:dairy" in product.get("categories_tags",[]) or "en:dairy" in product.get("allergens_tags", []) or "en:dairy" in product.get("traces_tags", []),

                        # 음식 카테고리 및 태그 추가 (기존 food-tags 기능 포함)
                        "categories": product.get("categories_tags", []),
                        "tags": product.get("ingredients_tags", []),
                    }
                    food_list.append(food_data)

                return Response(food_list, status=status.HTTP_200_OK)

        return Response({"error": "음식을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
