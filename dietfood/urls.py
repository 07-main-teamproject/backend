from django.urls import path
from .views import DietFoodAddView,DietFoodRemoveView,DietFoodUpdatePortionSizeView

urlpatterns = [
    path('add/<int:diet_id>/', DietFoodAddView.as_view(), name='dietfood-add'),  # 음식 추가
    path('remove/<int:diet_id>/', DietFoodRemoveView.as_view(), name='dietfood-remove'),  # 음식 제거
    path('protionsize/<int:diet_id>/', DietFoodUpdatePortionSizeView.as_view(), name='dietfood-protionsize'), # 양 수정
]