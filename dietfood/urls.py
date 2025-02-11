from django.urls import path
from .views import DietFoodView

urlpatterns = [
    path("", DietFoodView.as_view(), name="diet-food-api"),
]
