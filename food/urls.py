from django.urls import path
from .views import FoodInfoView

urlpatterns = [
    path("info/", FoodInfoView.as_view(), name="food-info"),
]