from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
import requests


class FoodInfoView(APIView):
    def get(self, request):
        query = request.query_params.get("query")  # 사용자가 입력한 query를 가져옴 예:?query=banana
        # 검색어가 없을 경우 에러 반환
        if not query:
            return Response({"error": "음식 이름을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 캐시에서 데이터 확인
        cache_key = f"food_info_{query}" # 검색어를 이용해 캐시 키 생성 (food_info_banana)
        cached_data = cache.get(cache_key) # 이미 캐시에 저장된 데이터가 있으면 가져옴
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)  # 캐싱된 데이터 반환

        # 캐시에 없으면 OpenFoodFacts 검색 API 호출
        search_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1"
        try:
            search_response = requests.get(search_url, timeout=20)  # 타임아웃  설정 (시간 초과 방지)
            search_response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
            search_data = search_response.json() # 정상적으로 가져오면 search_data에 저장됨
            # 외부 api 요청이 실패한 경우 예외 처리
        except requests.exceptions.Timeout:
            return Response({"error": "외부 API 응답이 너무 느립니다."}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.exceptions.RequestException:
            return Response({"error": "외부 API 요청 실패"}, status=status.HTTP_502_BAD_GATEWAY)

        # api 응답 데이터에서 음식 정보 추출
        if search_response.status_code == 200:
            products = search_data.get("products", []) # api 응답에서 products 리스트를 가져옴

            if products:
                food_list = []
                # 최대 3개의 유사한 음식 반환 예: banana 검색하면 관련된 3가지 음식 반환
                for product in products[:3]:
                    # 각 음식의 id, 이름, 칼로리, 단백질, 탄수화물, 지방 값을 가져옴
                    food_data = {
                        "id": product.get("code", None),
                        "name": product.get("product_name", query),
                        "calories": product.get("nutriments", {}).get("energy-kcal", 0),
                        "protein": product.get("nutriments", {}).get("proteins", 0),
                        "carbs": product.get("nutriments", {}).get("carbohydrates", 0),
                        "fat": product.get("nutriments", {}).get("fat", 0),

                        # 해당 음식이 가진 모든 태그(4가지) 중 `견과류`, `글루텐`, `유제품` 포함 여부 확인 -> True 또는 False 값을 반환
                        "contains_nuts": "en:nuts" in product.get("ingredients_tags", []) or "en:nuts" in product.get("categories_tags", []) or "en:nuts" in product.get("allergens_tags", []) or "en:nuts" in product.get("traces_tags", []),
                        "contains_gluten": "en:gluten" in product.get("ingredients_tags",[]) or "en:gluten" in product.get("categories_tags", []) or "en:gluten" in product.get("allergens_tags",[]) or "en:gluten" in product.get("traces_tags", []),
                        "contains_dairy": "en:dairy" in product.get("ingredients_tags",[]) or "en:dairy" in product.get("categories_tags",[]) or "en:dairy" in product.get("allergens_tags", []) or "en:dairy" in product.get("traces_tags", []),

                        # 음식이 속한 카테고리 , 주요 성분 태그 (포함 여부 판단 x, 정보 제공 목적 o)
                        "categories": product.get("categories_tags", []), # 예: 빵, 과자, 육류 등
                        "tags": product.get("ingredients_tags", []),      # # 예: 밀가루, 설탕, 이스트 등
                    }
                    food_list.append(food_data)

                cache.set(cache_key, food_list, timeout=3600)  # 캐시에 데이터 저장 (60분 = 3600초)


                return Response(food_list, status=status.HTTP_200_OK) # 정상적으로 검색된 음식 정보를 응답으로 반환

        return Response({"error": "음식을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND) # 검색한 음식을 찾을 수 없으면 에러 반환

