from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from .models import Cook, Dish, DishType
from .forms import (
    DishSearchForm,
    CookSearchForm,
    DishTypeSearchForm,
    CookCreationForm,
    CookExperienceUpdateForm,
    AssignCookToDishForm,
    DishForm,
)

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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = DishTypeSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        queryset = DishType.objects.all()
        form = DishTypeSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset

class DishListView(generic.ListView):
    model = Dish
    template_name = "kitchen/dish_list.html"
    context_object_name = "dish_list"
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = DishSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        queryset = Dish.objects.select_related("dish_type")
        form = DishSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset

class CookListView(generic.ListView):
    model = Cook
    template_name = "kitchen/cook_list.html"
    context_object_name = "cook_list"
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.GET.get("username", "")
        context["search_form"] = CookSearchForm(initial={"username": username})
        return context

    def get_queryset(self):
        queryset = Cook.objects.all()
        form = CookSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(username__icontains=form.cleaned_data["username"])
        return queryset

class DishDetailView(LoginRequiredMixin, generic.DetailView):
    model = Dish

    def get_queryset(self):
        return Dish.objects.prefetch_related("cooks", "ingredients")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dish: Dish = self.get_object()
        user = self.request.user
        if user.is_authenticated and getattr(user, "can_assign_others", False):
            context["assign_form"] = AssignCookToDishForm(dish=dish, user=user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        dish: Dish = self.object
        user = request.user
        if not user.is_authenticated or not getattr(user, "can_assign_others", False):
            return HttpResponseRedirect(request.path)
        form = AssignCookToDishForm(request.POST, dish=dish, user=user)
        if form.is_valid():
            cook = form.cleaned_data["cook"]
            dish.cooks.add(cook)
            return HttpResponseRedirect(request.path)
        context = self.get_context_data(object=dish)
        context["assign_form"] = form
        return self.render_to_response(context)

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

class DishTypeCreateView(UserPassesTestMixin, generic.CreateView):
    model = DishType
    fields = "__all__"
    template_name = "kitchen/dish_type_form.html"
    success_url = reverse_lazy("kitchen:dish-type-list")

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, "can_manage_types", False)

class DishTypeUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = DishType
    fields = "__all__"
    template_name = "kitchen/dish_type_form.html"
    success_url = reverse_lazy("kitchen:dish-type-list")

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, "can_manage_types", False)

class DishTypeDeleteView(UserPassesTestMixin, generic.DeleteView):
    model = DishType
    template_name = "kitchen/dish_type_confirm_delete.html"
    success_url = reverse_lazy("kitchen:dish-type-list")

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, "can_manage_types", False)

class DishCreateView(UserPassesTestMixin, generic.CreateView):
    model = Dish
    form_class = DishForm
    template_name = "kitchen/dish_form.html"
    success_url = reverse_lazy("kitchen:dish-list")

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, "can_manage_dishes", False)

class DishUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = Dish
    form_class = DishForm
    template_name = "kitchen/dish_form.html"
    success_url = reverse_lazy("kitchen:dish-list")

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, "can_manage_dishes", False)

class DishDeleteView(UserPassesTestMixin, generic.DeleteView):
    model = Dish
    template_name = "kitchen/dish_confirm_delete.html"
    success_url = reverse_lazy("kitchen:dish-list")

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, "can_manage_dishes", False)

class CookCreateView(LoginRequiredMixin, generic.CreateView):
    model = Cook
    form_class = CookCreationForm
    template_name = "kitchen/cook_form.html"
    success_url = reverse_lazy("kitchen:cook-list")

class CookUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Cook
    form_class = CookExperienceUpdateForm
    template_name = "kitchen/cook_form.html"
    success_url = reverse_lazy("kitchen:cook-list")

class CookDeleteView(UserPassesTestMixin, generic.DeleteView):
    model = Cook
    template_name = "kitchen/cook_confirm_delete.html"
    success_url = reverse_lazy("kitchen:cook-list")

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, "is_chef", False)

@login_required
def toggle_assign_to_dish(request, pk):
    cook = Cook.objects.get(id=request.user.id)
    dish = get_object_or_404(Dish, id=pk)
    if cook in dish.cooks.all():
        dish.cooks.remove(cook)
    else:
        dish.cooks.add(cook)
    return HttpResponseRedirect(reverse_lazy("kitchen:dish-detail", kwargs={"pk": pk}))
