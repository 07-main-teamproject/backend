from django.urls import path
from .views import DietListView,DietCreateView,DietUpdateView,DietDeleteView
from dietfood.views import DietFoodAddView,DietFoodRemoveView,DietFoodUpdatePortion_sizeView

urlpatterns = [
    path('', DietListView.as_view(), name='diet-list'),  # 사용자의 식단 목록 조회
    path('create/', DietCreateView.as_view(), name='diet-create'),  # 새로운 식단 생성
    path('<int:diet_id>/update/', DietUpdateView.as_view(), name='diet-update'),  # 식단 수정 (음식 추가/제거)
    path('<int:diet_id>/delete/', DietDeleteView.as_view(), name='diet-delete'),  # 식단 삭제

# dietfood 관련 경로 (음식 추가, 제거, 수량 수정)
    path('<int:diet_id>/add-food/', DietFoodAddView.as_view(), name='dietfood-add'),  # 음식 추가
    path('<int:diet_id>/remove-food/', DietFoodRemoveView.as_view(), name='dietfood-remove'),  # 음식 제거
    path('<int:diet_id>/update-food-quantity/', DietFoodUpdatePortion_sizeView.as_view(), name='dietfood-update-portion_size'),  # 양(그람) 수정
]