from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Recipe


class RecipeListTests(TestCase):
    """Tests for the recipe list on the home page."""

    def setUp(self):
        self.user = User.objects.create_user("cook", password="pass12345")

    def make_recipe(self, title, status="approved"):
        """Create a recipe with all required fields."""
        return Recipe.objects.create(
            author=self.user,
            title=title,
            description="Test description",
            ingredients="Flour\nEggs",
            method="Mix\nBake",
            servings=2,
            prep_time=10,
            cook_time=20,
            difficulty="easy",
            status=status,
        )

    def test_only_approved_recipes_are_listed(self):
        self.make_recipe("Visible Soup")
        self.make_recipe("Hidden Stew", status="pending")
        response = self.client.get(reverse("index"))
        self.assertContains(response, "Visible Soup")
        self.assertNotContains(response, "Hidden Stew")

    def test_list_is_paginated_six_per_page(self):
        for number in range(7):
            self.make_recipe(f"Recipe {number}")
        response = self.client.get(reverse("index"))
        self.assertEqual(len(response.context["page_obj"]), 6)
        response = self.client.get(reverse("index") + "?page=2")
        self.assertEqual(len(response.context["page_obj"]), 1)