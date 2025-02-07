from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests


class FoodInfoView(APIView):
    def get(self, request):
        query = request.query_params.get("query")
        if not query:
            return Response({"error": "음식 이름을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        # OpenFoodFacts 검색 API 호출
        search_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1"
        search_response = requests.get(search_url)

        if search_response.status_code == 200:
            search_data = search_response.json()
            products = search_data.get("products", [])
            if products:
                product = products[0]  # 첫 번째 검색 결과 사용

                # 알레르기 관련 태그들 (중복 확인)
                allergens = product.get("allergens_tags", [])
                traces = product.get("traces_tags", [])
                categories = product.get("categories_tags", [])
                ingredients = product.get("ingredients_tags", [])

                return Response({
                    "id": product.get("code", None),
                    "name": product.get("product_name", query),
                    "calories": product.get("nutriments", {}).get("energy-kcal", 0),
                    "protein": product.get("nutriments", {}).get("proteins", 0),
                    "carbs": product.get("nutriments", {}).get("carbohydrates", 0),
                    "fat": product.get("nutriments", {}).get("fat", 0),

                    #  `nuts`, `gluten`, `dairy` 포함 여부 확인 (여러 필드 검사)
                    "contains_nuts": (
                            "en:nuts" in ingredients or
                            "en:nuts" in categories or
                            "en:nuts" in allergens or
                            "en:nuts" in traces
                    ),
                    "contains_gluten": (
                            "en:gluten" in ingredients or
                            "en:gluten" in categories or
                            "en:gluten" in allergens or
                            "en:gluten" in traces
                    ),
                     "contains_dairy": (
                        "en:dairy" in ingredients or
                        "en:dairy" in categories or
                        "en:dairy" in allergens or
                        "en:dairy" in traces
                    )
                }, status=status.HTTP_200_OK)

        return Response({"error": "음식을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

