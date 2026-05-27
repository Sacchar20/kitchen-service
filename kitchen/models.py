from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class DishType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Cook(AbstractUser):
    years_of_experience = models.IntegerField(
        validators=[
            MinValueValidator(0, message="Years of experience cannot be negative.")
        ]
    )
    is_sub_chef = models.BooleanField(default=False)

    class Meta:
        verbose_name = "cook"
        verbose_name_plural = "cooks"

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"

    def clean(self):
        super().clean()

        if self.years_of_experience is not None:
            if (self.is_staff or self.is_superuser) and self.years_of_experience < 10:
                raise ValidationError(
                    {
                        "years_of_experience": "Chef must have at least 10 years of experience."
                    }
                )

            if self.is_sub_chef and self.years_of_experience < 5:
                raise ValidationError(
                    {
                        "years_of_experience": "Sub-chef must have at least 5 years of experience."
                    }
                )
        else:
            if self.is_staff or self.is_superuser or self.is_sub_chef:
                raise ValidationError(
                    {
                        "years_of_experience": "Years of experience is required for this role."
                    }
                )

    @property
    def role_name(self):
        if self.is_staff or self.is_superuser:
            return "Chef"
        if self.is_sub_chef:
            return "Sous Chef"
        if self.years_of_experience is not None and self.years_of_experience >= 5:
            return "Senior Cook"
        return "Junior Cook"

    @property
    def is_chef(self):
        return self.is_staff or self.is_superuser

    @property
    def has_high_experience(self):
        return self.years_of_experience is not None and self.years_of_experience >= 5

    @property
    def can_manage_types(self):
        return self.is_chef

    @property
    def can_manage_dishes(self):
        return self.is_chef or self.is_sub_chef

    @property
    def can_assign_others(self):
        return self.is_chef or self.is_sub_chef or self.has_high_experience


class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    dish_type = models.ForeignKey(
        DishType, on_delete=models.CASCADE, related_name="dishes"
    )
    ingredients = models.ManyToManyField(Ingredient, related_name="dishes")
    cooks = models.ManyToManyField(Cook, related_name="dishes")

    class Meta:
        verbose_name_plural = "dishes"
        ordering = ["name"]

    def __str__(self):
        return self.name
