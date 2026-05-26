from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from kitchen.models import DishType, Dish

INDEX_URL = reverse("kitchen:index")
DISH_LIST_URL = reverse("kitchen:dish-list")


class PublicKitchenTests(TestCase):

    def test_homepage_accessible_without_login(self):
        response = self.client.get(INDEX_URL)
        self.assertEqual(response.status_code, 200)

    def test_dish_list_accessible_without_login(self):
        response = self.client.get(DISH_LIST_URL)
        self.assertEqual(response.status_code, 200)

    def test_dish_detail_redirects_to_login(self):
        dish_type = DishType.objects.create(name="Dessert")
        dish = Dish.objects.create(
            name="Test Cake",
            description="Yummy dessert",
            price=10.00,
            dish_type=dish_type
        )
        detail_url = reverse("kitchen:dish-detail", kwargs={"pk": dish.pk})
        response = self.client.get(detail_url)
        login_url = reverse("login") + f"?next={detail_url}"
        self.assertRedirects(response, login_url)


class PrivateKitchenTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_cook",
            password="strong_password123",
            years_of_experience=3
        )
        self.client.login(username="test_cook", password="strong_password123")
        self.dish_type = DishType.objects.create(name="Pizzas")
        self.dish = Dish.objects.create(
            name="Margherita",
            description="Classic pizza",
            price=12.50,
            dish_type=self.dish_type
        )

    def test_dish_detail_accessible_with_login(self):
        detail_url = reverse("kitchen:dish-detail", kwargs={"pk": self.dish.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.dish.name)

    def test_search_dish_by_name(self):
        Dish.objects.create(
            name="Pepperoni",
            description="Spicy",
            price=15.00,
            dish_type=self.dish_type
        )
        response = self.client.get(DISH_LIST_URL, {"name": "Margh"})
        self.assertIn(self.dish, response.context["dish_list"])
        self.assertEqual(len(response.context["dish_list"]), 1)

    def test_toggle_assign_to_dish_adds_cook(self):
        toggle_url = reverse("kitchen:toggle-assign", kwargs={"pk": self.dish.pk})
        response = self.client.get(toggle_url)
        self.assertRedirects(response, reverse("kitchen:dish-detail", kwargs={"pk": self.dish.pk}))
        self.assertIn(self.user, self.dish.cooks.all())

    def test_toggle_assign_to_dish_removes_cook(self):
        self.dish.cooks.add(self.user)
        toggle_url = reverse("kitchen:toggle-assign", kwargs={"pk": self.dish.pk})
        response = self.client.get(toggle_url)
        self.assertRedirects(response, reverse("kitchen:dish-detail", kwargs={"pk": self.dish.pk}))
        self.assertNotIn(self.user, self.dish.cooks.all())

    def test_pagination_is_five(self):
        for i in range(7):
            Dish.objects.create(
                name=f"Dish {i}",
                description="Test",
                price=10.00,
                dish_type=self.dish_type
            )
        response = self.client.get(DISH_LIST_URL)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["dish_list"]), 5)

    def test_cook_cannot_create_dish_type_get(self):
        create_url = reverse("kitchen:dish-type-create")
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 403)

    def test_cook_cannot_create_dish_type_post(self):
        create_url = reverse("kitchen:dish-type-create")
        response = self.client.get(create_url, data={"name": "New Type"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(DishType.objects.filter(name="New Type").count(), 0)


class CookModelValidationTests(TestCase):

    def test_chef_validation_raises_error_if_low_experience(self):
        chef = get_user_model()(
            username="bad_chef",
            is_staff=True,
            years_of_experience=5
        )
        with self.assertRaises(ValidationError):
            chef.clean()

    def test_chef_validation_passes_if_high_experience(self):
        chef = get_user_model()(
            username="good_chef",
            is_staff=True,
            years_of_experience=12
        )
        try:
            chef.clean()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly!")

    def test_sub_chef_validation_raises_error_if_low_experience(self):
        sub_chef = get_user_model()(
            username="bad_sub_chef",
            is_sub_chef=True,
            years_of_experience=2
        )
        with self.assertRaises(ValidationError):
            sub_chef.clean()

    def test_sub_chef_validation_passes_if_high_experience(self):
        sub_chef = get_user_model()(
            username="good_sub_chef",
            is_sub_chef=True,
            years_of_experience=6
        )
        try:
            sub_chef.clean()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly!")

    def test_experience_cannot_be_negative(self):
        cook = get_user_model()(
            username="negative_cook",
            years_of_experience=-1
        )
        with self.assertRaises(ValidationError):
            cook.full_clean()
