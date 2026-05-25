from django.shortcuts import render
from django.views import generic
from .models import Cook, Dish, DishType


def index(request):
    num_cooks = Cook.objects.count()
    num_dishes = Dish.objects.count()
    num_dish_types = DishType.objects.count()

    context = {
        "num_cooks": num_cooks,
        "num_dishes": num_dishes,
        "num_dish_types": num_dish_types,
    }

    return render(request, "kitchen/index.html", context=context)


class DishTypeListView(generic.ListView):
    model = DishType
    context_object_name = "dish_type_list"
    template_name = "kitchen/dish_type_list.html"
    paginate_by = 5


class DishListView(generic.ListView):
    model = Dish
    template_name = "kitchen/dish_list.html"
    context_object_name = "dish_list"
    paginate_by = 5

    def get_queryset(self):
        return Dish.objects.select_related("dish_type")


class CookListView(generic.ListView):
    model = Cook
    template_name = "kitchen/cook_list.html"
    context_object_name = "cook_list"
    paginate_by = 5


class DishDetailView(generic.DetailView):
    model = Dish

    def get_queryset(self):
        return Dish.objects.prefetch_related("cooks")


class CookDetailView(generic.DetailView):
    model = Cook

    def get_queryset(self):
        return Cook.objects.prefetch_related("dishes")


class DishTypeDetailView(generic.DetailView):
    model = DishType
    template_name = "kitchen/dish_type_detail.html"
    context_object_name = "dish_type"

    def get_queryset(self):
        return DishType.objects.prefetch_related("dishes")
