from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Recipe


class RecipeListTests(TestCase):
    """Tests for the recipe list on the home page."""

    def setUp(self):
        self.user = User.objects.create_user("cook", password="pass12345")

    def make_recipe(
        self, title, status="approved", category="dinner", difficulty="easy"
    ):
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
            category=category,
            difficulty=difficulty,
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

    def test_category_and_difficulty_filters_are_applied(self):
        self.make_recipe("Dinner Pasta", category="dinner", difficulty="easy")
        self.make_recipe("Dessert Cake", category="dessert", difficulty="hard")

        response = self.client.get(
            reverse("index"),
            {"category": "dinner", "difficulty": "easy"},
        )

        self.assertContains(response, "Dinner Pasta")
        self.assertNotContains(response, "Dessert Cake")

    def test_name_sort_orders_recipes_alphabetically(self):
        self.make_recipe("Zesty Soup")
        self.make_recipe("Apple Tart")

        response = self.client.get(reverse("index"), {"sort": "name"})

        self.assertEqual(
            [recipe.title for recipe in response.context["page_obj"]],
            ["Apple Tart", "Zesty Soup"],
        )

    def test_most_liked_sort_and_my_liked_filter(self):
        popular = self.make_recipe("Popular Dish")
        personal = self.make_recipe("Personal Dish")
        other_user = User.objects.create_user(
            "another-cook",
            password="pass12345",
        )
        popular.liked_by.add(self.user, other_user)
        personal.liked_by.add(self.user)
        self.client.force_login(self.user)

        response = self.client.get(reverse("index"), {"sort": "likes"})
        self.assertEqual(response.context["page_obj"][0], popular)

        response = self.client.get(reverse("index"), {"liked": "1"})
        self.assertEqual(
            {recipe.title for recipe in response.context["page_obj"]},
            {"Popular Dish", "Personal Dish"},
        )

    def test_authenticated_user_can_toggle_recipe_like(self):
        recipe = self.make_recipe("Likeable Dish")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("toggle_recipe_like", args=[recipe.pk]),
            {"next": reverse("index")},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(recipe.liked_by.filter(pk=self.user.pk).exists())

        self.client.post(
            reverse("toggle_recipe_like", args=[recipe.pk]),
            {"next": reverse("index")},
        )
        self.assertFalse(recipe.liked_by.filter(pk=self.user.pk).exists())

    def test_like_toggle_requires_login(self):
        recipe = self.make_recipe("Protected Like")

        response = self.client.post(
            reverse("toggle_recipe_like", args=[recipe.pk]),
            {"next": reverse("index")},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account_login"), response.url)
        self.assertFalse(recipe.liked_by.exists())

    def test_like_toggle_rejects_unsafe_next_url(self):
        recipe = self.make_recipe("Safe Redirect Like")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("toggle_recipe_like", args=[recipe.pk]),
            {"next": "https://example.com/unsafe"},
        )

        self.assertRedirects(response, reverse("index"))

    def test_my_liked_filter_is_hidden_and_ignored_for_anonymous_users(self):
        self.make_recipe("Public Dish")

        response = self.client.get(reverse("index"), {"liked": "1"})

        self.assertNotContains(response, "My liked")
        self.assertContains(response, "Public Dish")
