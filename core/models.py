from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Recipe(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    ingredients = models.TextField()
    method = models.TextField()
    servings = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    prep_time = models.PositiveIntegerField(
        verbose_name="Prep time (minutes)",
        validators=[MinValueValidator(1)],
    )
    cook_time = models.PositiveIntegerField(
        verbose_name="Cook time (minutes)",
        validators=[MinValueValidator(1)],
    )
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.recipe.title}"