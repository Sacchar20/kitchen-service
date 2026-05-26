from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Cook, DishType, Ingredient, Dish


@admin.register(Cook)
class CookAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("years_of_experience", "is_sub_chef", "show_role")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Additional info", {"fields": ("years_of_experience", "is_sub_chef")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional info", {
            "fields": ("years_of_experience", "is_sub_chef", "first_name", "last_name")
        }),
    )

    @admin.display(description="Role")
    def show_role(self, obj):
        return obj.role_name


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "dish_type")
    list_filter = ("dish_type",)
    search_fields = ("name",)


admin.site.register(DishType)
admin.site.register(Ingredient)
