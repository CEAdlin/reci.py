from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from notifications.signals import notify


class NotificationInboxTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="notification-user",
            password="pass12345",
        )
        self.other_user = User.objects.create_user(
            username="other-notification-user",
            password="pass12345",
        )

    def send_notification(self, recipient, verb):
        notify.send(
            sender=self.user,
            recipient=recipient,
            verb=verb,
        )
        return recipient.notifications.unread().latest("timestamp")

    def test_inbox_requires_login(self):
        response = self.client.get(reverse("notifications_inbox"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account_login"), response.url)

    def test_inbox_shows_only_current_users_unread_notifications(self):
        own_notification = self.send_notification(
            self.user,
            "A notification for this user.",
        )
        other_notification = self.send_notification(
            self.other_user,
            "A notification for another user.",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("notifications_inbox"))

        self.assertContains(response, own_notification.verb)
        self.assertNotContains(response, other_notification.verb)

    def test_user_can_mark_own_notification_as_read(self):
        notification = self.send_notification(
            self.user,
            "Read this notification.",
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("notifications_inbox"),
            {"mark_read": notification.pk},
        )

        self.assertRedirects(response, reverse("notifications_inbox"))
        self.assertFalse(
            self.user.notifications.unread()
            .filter(pk=notification.pk)
            .exists()
        )

    def test_user_cannot_mark_another_users_notification_as_read(self):
        notification = self.send_notification(
            self.other_user,
            "Private notification.",
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("notifications_inbox"),
            {"mark_read": notification.pk},
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            self.other_user.notifications.unread()
            .filter(pk=notification.pk)
            .exists()
        )
