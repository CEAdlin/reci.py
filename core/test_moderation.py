from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Comment, Recipe


class ModerationWorkflowTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="moderation-author",
            password="pass12345",
        )
        self.commenter = User.objects.create_user(
            username="moderation-commenter",
            password="pass12345",
        )
        self.staff = User.objects.create_user(
            username="reviewer",
            password="pass12345",
            is_staff=True,
        )
        self.recipe_data = {
            "description": "A recipe for moderation tests.",
            "ingredients": "Flour\nEggs",
            "method": "Mix\nBake",
            "servings": 2,
            "prep_time": 10,
            "cook_time": 20,
            "category": Recipe.Category.DINNER,
            "difficulty": Recipe.Difficulty.EASY,
        }

    def make_recipe(self, title, status=Recipe.Status.PENDING):
        return Recipe.objects.create(
            author=self.author,
            title=title,
            status=status,
            **self.recipe_data,
        )

    def make_comment(self, recipe, approved=False):
        return Comment.objects.create(
            recipe=recipe,
            author=self.commenter,
            body="A pending comment.",
            approved=approved,
        )

    def test_non_staff_cannot_access_moderation_pages(self):
        recipe = self.make_recipe("Restricted Recipe")
        self.client.force_login(self.author)

        for view_name, args in (
            ("recipe_admin", ()),
            ("recipe_review", ()),
            ("comment_review", ()),
            ("recipe_approve", (recipe.pk,)),
        ):
            response = self.client.get(reverse(view_name, args=args))
            self.assertEqual(response.status_code, 302)

    def test_staff_can_review_recipe_and_approve_it(self):
        recipe = self.make_recipe("Recipe To Approve")
        self.client.force_login(self.staff)

        review_response = self.client.get(reverse("recipe_review"))
        approve_response = self.client.post(
            reverse("recipe_approve", args=[recipe.pk])
        )

        self.assertEqual(review_response.status_code, 200)
        self.assertEqual(approve_response.status_code, 302)
        self.assertEqual(approve_response.url, reverse("recipe_review"))
        recipe.refresh_from_db()
        self.assertEqual(recipe.status, Recipe.Status.APPROVED)
        notification = self.author.notifications.unread().first()
        self.assertIsNotNone(notification)
        self.assertIn("was approved", notification.verb)

    def test_staff_can_reject_recipe(self):
        recipe = self.make_recipe("Recipe To Reject")
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("recipe_reject", args=[recipe.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("recipe_review"))
        recipe.refresh_from_db()
        self.assertEqual(recipe.status, Recipe.Status.REJECTED)
        self.assertTrue(self.author.notifications.unread().exists())

    def test_staff_can_approve_comment(self):
        recipe = self.make_recipe("Recipe With Comment")
        comment = self.make_comment(recipe)
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("comment_approve", args=[comment.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("comment_review"))
        comment.refresh_from_db()
        self.assertTrue(comment.approved)
        self.assertTrue(self.commenter.notifications.unread().exists())

    def test_staff_can_reject_comment(self):
        recipe = self.make_recipe("Recipe With Rejected Comment")
        comment = self.make_comment(recipe)
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("comment_reject", args=[comment.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("comment_review"))
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())
        self.assertTrue(self.commenter.notifications.unread().exists())
