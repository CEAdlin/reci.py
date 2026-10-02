from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Recipe


class ProfileRecipeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profile-user",
            password="pass12345",
        )
        self.other_user = User.objects.create_user(
            username="other-user",
            password="pass12345",
        )
        self.recipe_data = {
            "description": "A recipe description.",
            "ingredients": "Flour\nEggs",
            "method": "Mix\nBake",
            "servings": 2,
            "prep_time": 10,
            "cook_time": 20,
            "category": Recipe.Category.DINNER,
            "difficulty": Recipe.Difficulty.EASY,
        }

    def make_recipe(self, author, title, status):
        return Recipe.objects.create(
            author=author,
            title=title,
            status=status,
            **self.recipe_data,
        )

    def test_profile_shows_own_pending_recipe_with_owner_actions(self):
        recipe = self.make_recipe(
            self.user,
            "Pending Pasta",
            Recipe.Status.PENDING,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("profile"))

        self.assertContains(response, "profile-user's Profile")
        self.assertContains(response, recipe.title)
        self.assertContains(
            response,
            reverse("edit_recipe", args=[recipe.pk]),
        )
        self.assertContains(
            response,
            reverse("delete_recipe", args=[recipe.pk]),
        )
        self.assertContains(response, "Awaiting approval")
        self.assertNotContains(
            response,
            f'href="{reverse("recipe_detail", args=[recipe.pk])}"',
        )

    def test_profile_shows_owned_and_liked_public_recipes_newest_first(self):
        older = self.make_recipe(
            self.user,
            "Older Dinner",
            Recipe.Status.APPROVED,
        )
        newer = self.make_recipe(
            self.user,
            "Newer Dinner",
            Recipe.Status.PUBLISHED,
        )
        liked = self.make_recipe(
            self.other_user,
            "Liked Dinner",
            Recipe.Status.PUBLISHED,
        )
        liked.liked_by.add(self.user)
        self.client.force_login(self.user)

        response = self.client.get(reverse("profile"))
        content = response.content.decode()

        self.assertContains(response, older.title)
        self.assertContains(response, newer.title)
        self.assertContains(response, liked.title)
        self.assertLess(content.index(newer.title), content.index(older.title))
        self.assertContains(response, "Update User Profile")
        self.assertContains(response, reverse("account_reset_password"))

    def test_profile_does_not_show_another_users_pending_recipe(self):
        recipe = self.make_recipe(
            self.other_user,
            "Someone Elses Pending Recipe",
            Recipe.Status.PENDING,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("profile"))

        self.assertNotContains(response, recipe.title)

    def test_user_can_update_profile_email(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("profile"),
            {"email": "new-address@example.com"},
        )

        self.assertRedirects(response, reverse("profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new-address@example.com")

    def test_invalid_profile_email_is_not_saved(self):
        self.user.email = "old-address@example.com"
        self.user.save()
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("profile"),
            {"email": "not-an-email"},
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "old-address@example.com")
