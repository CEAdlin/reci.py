from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from .forms import RecipeForm
from .models import Recipe


class RecipeSubmissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="homecook",
            password="test-password",
        )
        cls.valid_recipe = {
            "title": "Warm tomato tart",
            "description": "A simple savoury tart.",
            "ingredients": "Tomatoes\nPuff pastry",
            "method": "Bake until golden.",
            "servings": 4,
            "prep_time": 15,
            "cook_time": 30,
            "difficulty": Recipe.Difficulty.EASY,
        }

    def test_submission_page_requires_login(self):
        response = self.client.get(reverse("submit_recipe"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_form_requires_all_recipe_fields(self):
        form = RecipeForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEqual(
            set(form.errors),
            {
                "title",
                "description",
                "ingredients",
                "method",
                "servings",
                "prep_time",
                "cook_time",
                "difficulty",
            },
        )

    def test_form_rejects_non_positive_numbers(self):
        form_data = {**self.valid_recipe, "servings": 0, "prep_time": 0, "cook_time": -1}
        form = RecipeForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("servings", form.errors)
        self.assertIn("prep_time", form.errors)
        self.assertIn("cook_time", form.errors)

    def test_titles_must_be_unique(self):
        Recipe.objects.create(author=self.user, **self.valid_recipe)
        form = RecipeForm(data=self.valid_recipe)

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_authenticated_submission_is_saved_as_pending(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("submit_recipe"),
            data=self.valid_recipe,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("index"))
        recipe = Recipe.objects.get(title=self.valid_recipe["title"])
        self.assertEqual(recipe.author, self.user)
        self.assertEqual(recipe.status, Recipe.Status.PENDING)
        self.assertIn(
            "submitted and is awaiting review",
            str(list(get_messages(response.wsgi_request))[0]),
        )