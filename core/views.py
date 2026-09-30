from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CommentForm, ProfileForm, RecipeForm
from .models import Comment, Recipe


def index(request):
    """View for the home page"""
    return render(
        request,
        "core/index.html",
    )


@login_required
def profile(request):
    """View for the profile page"""

    if request.method == "POST":
        form = ProfileForm(data=request.POST)
        if form.is_valid():
            request.user.email = form.cleaned_data["email"]
            request.user.save()
            messages.add_message(
                request, messages.SUCCESS,
                f'Email address changed to {request.user.email}'
            )

    else:
        form = ProfileForm(initial={"email": request.user.email})

    return render(
        request,
        "core/profile.html",
        {
            "form": form,
        }
    )


@login_required
def submit_recipe(request):
    """Allow authenticated users to submit a recipe for review."""
    if request.method == "POST":
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.status = recipe.Status.PENDING
            recipe.save()
            messages.success(
                request,
                "Your recipe has been submitted and is awaiting review.",
            )
            return redirect("index")
    else:
        form = RecipeForm()

    return render(request, "core/submit_recipe.html", {"form": form})

    def recipe_detail(request, pk):
    """Display recipe details and handle new comment submission."""
    recipe = get_object_or_404(Recipe, pk=pk)
    comments = recipe.comments.all()
    comment_form = CommentForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to leave a comment.")
            return redirect("recipe_detail", pk=pk)

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.recipe = recipe
            comment.save()
            messages.success(request, "Comment submitted successfully!")
            return redirect("recipe_detail", pk=pk)
        else:
            messages.error(request, "Error submitting comment. Please try again.")

    return render(
        request,
        "core/recipe_detail.html",
        {
            "recipe": recipe,
            "comments": comments,
            "comment_form": comment_form,
        },
    )


@login_required
def comment_edit(request, pk):
    """Allow comment author to edit their existing comment."""
    comment = get_object_or_404(Comment, pk=pk)

    if comment.author != request.user:
        messages.error(request, "You can only edit your own comments!")
        return redirect("recipe_detail", pk=comment.recipe.pk)

    if request.method == "POST":
        comment_form = CommentForm(data=request.POST, instance=comment)
        if comment_form.is_valid():
            comment_form.save()
            messages.success(request, "Comment updated successfully!")
            return redirect("recipe_detail", pk=comment.recipe.pk)
        else:
            messages.error(request, "Error updating comment.")
    else:
        comment_form = CommentForm(instance=comment)

    return render(
        request,
        "core/comment_edit.html",
        {
            "comment_form": comment_form,
            "comment": comment,
        },
    )


@login_required
def comment_delete(request, pk):
    """Allow comment author to delete their comment."""
    comment = get_object_or_404(Comment, pk=pk)

    if comment.author != request.user:
        messages.error(request, "You can only delete your own comments!")
    else:
        comment.delete()
        messages.success(request, "Comment deleted successfully!")

    return redirect("recipe_detail", pk=comment.recipe.pk)
