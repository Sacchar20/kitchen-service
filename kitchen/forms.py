from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Cook, Dish


class DishTypeSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by name..."})
    )


class DishSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by name..."})
    )


class CookSearchForm(forms.Form):
    username = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by username..."})
    )


class CookCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Cook
        fields = UserCreationForm.Meta.fields + (
            "years_of_experience",
            "is_sub_chef",
            "first_name",
            "last_name",
        )

    def clean(self):
        cleaned_data = super().clean() or {}
        years_of_experience = cleaned_data.get("years_of_experience")
        is_sub_chef = cleaned_data.get("is_sub_chef")
        if is_sub_chef:
            if years_of_experience is None or int(years_of_experience) < 5:
                raise ValidationError({
                    "years_of_experience": "Sub-chef must have at least 5 years of experience."
                })
        return cleaned_data


class CookExperienceUpdateForm(forms.ModelForm):
    class Meta:
        model = Cook
        fields = ["years_of_experience", "first_name", "last_name"]
        widgets = {
            "years_of_experience": forms.NumberInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_years_of_experience(self):
        years_of_experience = self.cleaned_data.get("years_of_experience")
        if years_of_experience is not None and years_of_experience < 0:
            raise ValidationError("Experience cannot be negative.")
        if self.instance and self.instance.is_sub_chef:
            if years_of_experience is None or years_of_experience < 5:
                raise ValidationError("Sub-chef must have at least 5 years of experience.")
        return years_of_experience


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "dish_type": forms.Select(attrs={"class": "form-select"}),
            "ingredients": forms.SelectMultiple(attrs={"class": "form-control"}),
            "cooks": forms.SelectMultiple(attrs={"class": "form-control"}),
        }


class AssignCookToDishForm(forms.Form):
    cook = forms.ModelChoiceField(
        queryset=Cook.objects.none(),
        label="Select a cook to assign",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    def __init__(self, *args, **kwargs):
        dish = kwargs.pop("dish", None)
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if dish and user and user.is_authenticated:
            queryset = Cook.objects.exclude(id__in=dish.cooks.values_list("id", flat=True))
            if user.is_staff or user.is_superuser:
                self.fields["cook"].queryset = queryset
            elif user.is_sub_chef:
                self.fields["cook"].queryset = queryset.filter(is_staff=False, is_superuser=False)
            elif user.years_of_experience is not None and user.years_of_experience >= 5:
                self.fields["cook"].queryset = queryset.filter(years_of_experience__lt=5)
