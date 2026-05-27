from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase


class CookModelValidationTests(TestCase):

    def test_chef_validation_raises_error_if_low_experience(self):
        chef = get_user_model()(
            username="bad_chef", is_staff=True, years_of_experience=5
        )
        with self.assertRaises(ValidationError):
            chef.clean()

    def test_chef_validation_passes_if_high_experience(self):
        chef = get_user_model()(
            username="good_chef", is_staff=True, years_of_experience=12
        )
        try:
            chef.clean()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly!")

    def test_sub_chef_validation_raises_error_if_low_experience(self):
        sub_chef = get_user_model()(
            username="bad_sub_chef", is_sub_chef=True, years_of_experience=2
        )
        with self.assertRaises(ValidationError):
            sub_chef.clean()

    def test_sub_chef_validation_passes_if_high_experience(self):
        sub_chef = get_user_model()(
            username="good_sub_chef", is_sub_chef=True, years_of_experience=6
        )
        try:
            sub_chef.clean()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly!")

    def test_experience_cannot_be_negative(self):
        cook = get_user_model()(username="negative_cook", years_of_experience=-1)
        with self.assertRaises(ValidationError):
            cook.full_clean()
