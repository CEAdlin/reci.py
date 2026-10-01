from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Recipe


class EditDeleteRecipeTests(TestCase):
    """Tests for user story #9: edit or delete my recipe."""

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass12345")
        self.other = User.objects.create_user("other", password="pass12345")
        self.recipe = Recipe.objects.create(
            author=self.author,
            title="Bug-Free Brownies",
            description="Rich and fudgy.",
            ingredients="Chocolate\nButter",
            method="Melt\nBake",
            servings=4,
            prep_time=10,
            cook_time=25,
            difficulty="easy",
            status=Recipe.Status.APPROVED,
        )

    def edit_data(self, title="Bug-Free Brownies v2"):
        """Valid form data for editing the recipe."""
        return {
            "title": title,
            "image_url": "",
            "description": "Even fudgier.",
            "ingredients": "Chocolate\nButter\nSugar",
            "method": "Melt\nMix\nBake",
            "servings": 6,
            "prep_time": 15,
            "cook_time": 25,
            "difficulty": "medium",
        }

    def test_my_recipes_requires_login(self):
        response = self.client.get(reverse("my_recipes"))
        self.assertEqual(response.status_code, 302)

    def test_my_recipes_lists_only_own_recipes(self):
        Recipe.objects.create(
            author=self.other, title="Someone Else's Soup",
            description="x", ingredients="x", method="x",
            servings=1, prep_time=1, cook_time=1, difficulty="easy",
        )
        self.client.login(username="author", password="pass12345")
        response = self.client.get(reverse("my_recipes"))
        self.assertContains(response, "Bug-Free Brownies")
        self.assertNotContains(response, "Someone Else&#x27;s Soup")

    def test_author_sees_edit_and_delete_buttons(self):
        self.client.login(username="author", password="pass12345")
        response = self.client.get(
            reverse("recipe_detail", args=[self.recipe.pk])
        )
        self.assertContains(
            response,
            reverse("edit_recipe", args=[self.recipe.pk])
        )
        self.assertContains(
            response,
            reverse("delete_recipe", args=[self.recipe.pk])
        )

    def test_other_users_do_not_see_buttons(self):
        self.client.login(username="other", password="pass12345")
        response = self.client.get(
            reverse("recipe_detail", args=[self.recipe.pk])
        )
        self.assertNotContains(
            response,
            reverse("edit_recipe", args=[self.recipe.pk])
        )

    def test_author_can_edit_and_recipe_goes_back_to_pending(self):
        self.client.login(username="author", password="pass12345")
        response = self.client.post(
            reverse("edit_recipe", args=[self.recipe.pk]), self.edit_data()
        )
        self.assertRedirects(response, reverse("my_recipes"))
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, "Bug-Free Brownies v2")
        self.assertEqual(self.recipe.servings, 6)
        self.assertEqual(self.recipe.status, Recipe.Status.PENDING)

    def test_invalid_edit_shows_errors_and_saves_nothing(self):
        self.client.login(username="author", password="pass12345")
        data = self.edit_data()
        data["prep_time"] = 0
        response = self.client.post(
            reverse("edit_recipe", args=[self.recipe.pk]),
            data
        )
        self.assertEqual(response.status_code, 200)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, "Bug-Free Brownies")
        self.assertEqual(self.recipe.status, Recipe.Status.APPROVED)

    def test_other_user_cannot_edit(self):
        self.client.login(username="other", password="pass12345")
        response = self.client.post(
            reverse("edit_recipe", args=[self.recipe.pk]),
            self.edit_data("Hacked")
        )
        self.assertEqual(response.status_code, 403)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, "Bug-Free Brownies")

    def test_delete_asks_for_confirmation_first(self):
        self.client.login(username="author", password="pass12345")
        response = self.client.get(
            reverse("delete_recipe", args=[self.recipe.pk])
        )
        self.assertContains(response, "Yes, delete it")
        self.assertTrue(Recipe.objects.filter(pk=self.recipe.pk).exists())

    def test_author_can_delete(self):
        self.client.login(username="author", password="pass12345")
        response = self.client.post(
            reverse("delete_recipe", args=[self.recipe.pk])
        )
        self.assertRedirects(response, reverse("my_recipes"))
        self.assertFalse(Recipe.objects.filter(pk=self.recipe.pk).exists())

    def test_other_user_cannot_delete(self):
        self.client.login(username="other", password="pass12345")
        response = self.client.post(
            reverse("delete_recipe", args=[self.recipe.pk])
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Recipe.objects.filter(pk=self.recipe.pk).exists())

    def test_logged_out_user_is_sent_to_login(self):
        response = self.client.post(
            reverse("delete_recipe", args=[self.recipe.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account_login"), response.url)
        self.assertTrue(Recipe.objects.filter(pk=self.recipe.pk).exists())
