from django.contrib import admin
from .models import Comment, Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin settings for recipes."""
    list_display = ("title", "author", "status", "created_at")
    list_filter = ("status", "difficulty")
    search_fields = ("title",)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "recipe", "created_at")
    search_fields = ("body", "author__username")