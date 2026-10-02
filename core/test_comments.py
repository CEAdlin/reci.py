from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Comment, Recipe


class CommentWorkflowTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="recipe-author",
            password="pass12345",
        )
        self.commenter = User.objects.create_user(
            username="commenter",
            password="pass12345",
        )
        self.other_user = User.objects.create_user(
            username="other-user",
            password="pass12345",
        )
        self.recipe = Recipe.objects.create(
            author=self.author,
            title="Commentable Recipe",
            description="A recipe for comment tests.",
            ingredients="Flour\nEggs",
            method="Mix\nBake",
            servings=2,
            prep_time=10,
            cook_time=20,
            category=Recipe.Category.DINNER,
            difficulty=Recipe.Difficulty.EASY,
            status=Recipe.Status.PUBLISHED,
        )

    def make_comment(self, author, body="A useful comment.", approved=False):
        return Comment.objects.create(
            recipe=self.recipe,
            author=author,
            body=body,
            approved=approved,
        )

    def test_anonymous_comment_submission_is_rejected(self):
        response = self.client.post(
            reverse("recipe_detail", args=[self.recipe.pk]),
            {"body": "A comment from a visitor."},
        )

        self.assertRedirects(
            response,
            reverse("recipe_detail", args=[self.recipe.pk]),
        )
        self.assertFalse(Comment.objects.exists())

    def test_authenticated_comment_is_saved_pending_and_notifies_author(self):
        self.client.force_login(self.commenter)

        response = self.client.post(
            reverse("recipe_detail", args=[self.recipe.pk]),
            {"body": "This was delicious."},
        )

        self.assertRedirects(
            response,
            reverse("recipe_detail", args=[self.recipe.pk]),
        )
        comment = Comment.objects.get()
        self.assertEqual(comment.author, self.commenter)
        self.assertFalse(comment.approved)
        notification = self.author.notifications.unread().first()
        self.assertIsNotNone(notification)
        self.assertIn("commented on your recipe", notification.verb)

    def test_empty_comment_is_not_saved(self):
        self.client.force_login(self.commenter)

        response = self.client.post(
            reverse("recipe_detail", args=[self.recipe.pk]),
            {"body": "   "},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.exists())
        self.assertContains(
            response,
            "Error submitting comment. Please try again.",
        )

    def test_public_detail_hides_other_users_pending_comments(self):
        approved = self.make_comment(
            self.commenter,
            "Approved comment.",
            approved=True,
        )
        pending = self.make_comment(
            self.other_user,
            "Private pending comment.",
        )

        response = self.client.get(
            reverse("recipe_detail", args=[self.recipe.pk])
        )

        self.assertContains(response, approved.body)
        self.assertNotContains(response, pending.body)

    def test_commenter_can_see_own_pending_comment(self):
        comment = self.make_comment(self.commenter)
        self.client.force_login(self.commenter)

        response = self.client.get(
            reverse("recipe_detail", args=[self.recipe.pk])
        )

        self.assertContains(response, comment.body)

    def test_comment_owner_can_edit_comment(self):
        comment = self.make_comment(self.commenter)
        self.client.force_login(self.commenter)

        response = self.client.post(
            reverse("comment_edit", args=[comment.pk]),
            {"body": "Updated comment."},
        )

        self.assertRedirects(
            response,
            reverse("recipe_detail", args=[self.recipe.pk]),
        )
        comment.refresh_from_db()
        self.assertEqual(comment.body, "Updated comment.")

    def test_comment_owner_can_delete_comment(self):
        comment = self.make_comment(self.commenter)
        self.client.force_login(self.commenter)

        response = self.client.post(
            reverse("comment_delete", args=[comment.pk])
        )

        self.assertRedirects(
            response,
            reverse("recipe_detail", args=[self.recipe.pk]),
        )
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_other_user_cannot_edit_or_delete_comment(self):
        comment = self.make_comment(self.commenter)
        self.client.force_login(self.other_user)

        edit_response = self.client.post(
            reverse("comment_edit", args=[comment.pk]),
            {"body": "Unauthorised edit."},
        )
        delete_response = self.client.post(
            reverse("comment_delete", args=[comment.pk])
        )

        self.assertRedirects(
            edit_response,
            reverse("recipe_detail", args=[self.recipe.pk]),
        )
        self.assertRedirects(
            delete_response,
            reverse("recipe_detail", args=[self.recipe.pk]),
        )
        comment.refresh_from_db()
        self.assertEqual(comment.body, "A useful comment.")
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())
