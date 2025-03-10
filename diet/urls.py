from django.urls import path
from .views import DietListView,DietCreateView,DietDeleteView,DietDetailView


urlpatterns = [
    path('', DietListView.as_view(), name='diet-list'),  # 사용자의 식단 전체 목록 조회
    path('<int:diet_id>/', DietDetailView.as_view(), name='diet-detail'),  # 단일 조회 추가
    path('create/', DietCreateView.as_view(), name='diet-create'),  # 새로운 식단 생성
    path('delete/<int:diet_id>/', DietDeleteView.as_view(), name='diet-delete'),  # 단일 삭제

]