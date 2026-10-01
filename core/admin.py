from django.contrib import admin
from .models import Comment, Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin settings for recipes."""
    list_display = ("title", "author", "category", "status", "created_at")
    list_filter = ("status", "category", "difficulty")
    search_fields = ("title",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "recipe", "body", "approved", "created_at")
    list_filter = ("approved", "created_at")
    search_fields = ("body", "author__username")
    actions = ["approve_comments"]

    @admin.action(description="Approve selected comments")
    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
