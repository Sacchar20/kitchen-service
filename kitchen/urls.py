from django.urls import path
from .views import index, DishTypeListView, DishListView

urlpatterns = [
    path("", index, name="index"),
    path("dish-types/", DishTypeListView.as_view(), name="dish-type-list"),
    path("dishes/", DishListView.as_view(), name="dish-list"),
]

app_name = "kitchen"
