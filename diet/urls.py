from django.urls import path ,include
from .views import DietView

urlpatterns = [
    path("", DietView.as_view(), name="diet-api"),
    path("food/", include("dietfood.urls")),  # dietfood의 URL을 diet 내부로 포함!
]