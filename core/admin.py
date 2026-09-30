from django.contrib import admin
from .models import Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin settings for recipes."""
    list_display = ("title", "author", "status", "created_at")
    list_filter = ("status", "difficulty")
    search_fields = ("title",)