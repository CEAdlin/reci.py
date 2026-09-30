from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from .forms import CommentForm, ProfileForm, RecipeForm
from .models import Comment, Recipe
from notifications.signals import notify


def index(request):
    """Home page with searchable, filterable, sortable recipe cards."""
    query = request.GET.get("q", "").strip()
    difficulty = request.GET.get("difficulty", "")
    sort = request.GET.get("sort", "newest")
    recipes = Recipe.objects.filter(
        status__in=PUBLIC_RECIPE_STATUSES
    ).select_related("author")

    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if difficulty in Recipe.Difficulty.values:
        recipes = recipes.filter(difficulty=difficulty)

    sort_fields = {
        "newest": "-created_at",
        "oldest": "created_at",
        "title": "title",
        "shortest": "prep_time",
    }
    recipes = recipes.order_by(sort_fields.get(sort, "-created_at"))
    paginator = Paginator(recipes, 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "core/index.html",
        {
            "page_obj": page_obj,
            "difficulty_choices": Recipe.Difficulty.choices,
            "selected_difficulty": difficulty,
            "selected_sort": sort,
            "search_query": query,
        },
    )


def recipe_detail(request, pk):
    """Display a recipe after it has been approved for public viewing."""
    recipe = get_object_or_404(
        Recipe,
        pk=pk,
        status__in=PUBLIC_RECIPE_STATUSES,
    )
    ingredients = [
        ingredient.strip()
        for ingredient in recipe.ingredients.splitlines()
        if ingredient.strip()
    ]
    method_steps = [
        step.strip()
        for step in recipe.method.splitlines()
        if step.strip()
    ]
    return render(
        request,
        "core/recipe_detail.html",
        {
            "recipe": recipe,
            "ingredients": ingredients,
            "method_steps": method_steps,
        },
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
            notify.send(
                sender=request.user,
                recipient=request.user,
                verb=f'Your recipe "{recipe.title}" was submitted and is pending review.',
                target=recipe
            )
            messages.success(
                request,
                "Your recipe has been submitted and is awaiting review.",
            )
            return redirect("index")
    else:
        form = RecipeForm()

    return render(request, "core/submit_recipe.html", {"form": form})

# ==========================================
# NOTIFICATIONS SYSTEM VIEWS
# ==========================================

@login_required
def notifications_inbox(request):
    """Fulfill Acceptance Criteria: Lists messages and handles marking notifications as read."""
    # If user clicks "Mark as read", process the request
    notification_id = request.GET.get('mark_read')
    if notification_id:
        notification = get_object_or_404(request.user.notifications.unread(), id=notification_id)
        notification.mark_as_read()
        messages.success(request, "Notification marked as read.")
        return redirect('notifications_inbox')

    # Get all unread notifications for this user
    unread_notifications = request.user.notifications.unread()
    
    return render(
        request, 
        "core/notifications.html", 
        {"notifications": unread_notifications}
    )


# ==========================================
# INTEGRATED RECIPE DETAIL & COMMENT VIEWS
# ==========================================


def get_recipe_detail_context(recipe):
    """
    Get the context for displaying recipe detail.  This is also used
    for displaying recipes for review.
    """
    ingredients = [
        ingredient.strip()
        for ingredient in recipe.ingredients.splitlines()
        if ingredient.strip()
    ]
    method_steps = [
        step.strip()
        for step in recipe.method.splitlines()
        if step.strip()
    ]
    return {
        "recipe": recipe,
        "ingredients": ingredients,
        "method_steps": method_steps,
        "comments": recipe.comments.all(),
        "comment_form": CommentForm(),
    }


def recipe_detail(request, pk):
    """Display recipe details and handle new comment submission."""
    recipe = get_object_or_404(
        Recipe,
        pk=pk,
        status__in=[Recipe.Status.APPROVED, Recipe.Status.PUBLISHED],
    )
    context = get_recipe_detail_context(recipe)
    comments = recipe.comments.filter(approved=True).order_by("-created_at")
    comment_form = context["comment_form"]

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

            # USER STORY ACTION: Notify the recipe author when someone comments on it
            if recipe.author != request.user:
                notify.send(
                    sender=request.user,
                    recipient=recipe.author,
                    verb=f'{request.user.username} commented on your recipe "{recipe.title}".',
                    target=recipe
                )

            messages.success(request, "Comment submitted successfully!")
            return redirect("recipe_detail", pk=pk)
        else:
            messages.error(request, "Error submitting comment. Please try again.")

    context["comment_form"] = comment_form
    return render(request, "core/recipe_detail.html", context)


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


# ==========================================
# INTEGRATED STAFF APPROVAL VIEWS
# ==========================================


@staff_member_required
def recipe_admin(request):
    """Display links to review recipes and comments"""
    pending_recipe = \
        Recipe.objects.filter(status=Recipe.Status.PENDING).first()
    pending_comment = \
        Comment.objects.first()  # filter(status=Recipe.Status.PENDING).first()

    return render(
        request,
        "core/recipe_admin.html",
        {
            "review_recipes": pending_recipe is not None,
            "review_comments": pending_comment is not None,
        }
    )


@staff_member_required
def recipe_review(request):
    """
    Allow the admin to approve or deny recipes.
    Each time this is called it shows a recipe for review.
    """
    pending = Recipe.objects.filter(status=Recipe.Status.PENDING).first()
    if pending is None:
        return HttpResponseRedirect(reverse('recipe_admin'))
    else:
        context = get_recipe_detail_context(pending)
        context["approval"] = True
        return render(request, "core/recipe_detail.html", context)


@staff_member_required
def comment_review(request):
    """
    Allow the admin to approve or deny comments.
    Each time this is called it shows a recipe with a pending comment.
    """
    pending = \
        Comment.objects.first()  # filter(status=Recipe.Status.PENDING).first()
    if pending is None:
        return HttpResponseRedirect(reverse('recipe_admin'))
    else:
        context = get_recipe_detail_context(pending.recipe)
        return render(request, "core/recipe_detail.html", context)


@staff_member_required
def recipe_approve(request, pk):
    """Approve a recipe"""
    if request.method == "POST":
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe.status = Recipe.Status.APPROVED
        recipe.save()
        messages.add_message(
            request, messages.SUCCESS,
            f'{recipe.title} was approved.'
        )

        # USER STORY ACTION: Notify author when their recipe is approved
        notify.send(
            sender=request.user,
            recipient=recipe.author,
            verb=f'Your recipe "{recipe.title}" was approved!',
            target=recipe
        )

    return HttpResponseRedirect(reverse('recipe_review'))


@staff_member_required
def recipe_reject(request, pk):
    """Reject a recipe"""
    if request.method == "POST":
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe.status = Recipe.Status.REJECTED
        recipe.save()
        messages.add_message(
            request, messages.SUCCESS,
            f'{recipe.title} was rejected.'
        )

        # USER STORY ACTION: Notify author when their recipe is rejected
        notify.send(
            sender=request.user,
            recipient=recipe.author,
            verb=f'Your recipe "{recipe.title}" was rejected.',
            target=recipe
        )

    return HttpResponseRedirect(reverse('recipe_review'))


@staff_member_required
def comment_approve(request, pk):
    """Approve a comment"""
    if request.method == "POST":
        comment = get_object_or_404(Comment, pk=pk)
        # comment.status = Comment.Status.APPROVED
        # comment.save()
        messages.add_message(
            request, messages.SUCCESS,
            f'Comment by {comment.author} approved.'
        )

        # USER STORY ACTION: Notify author when their comment is approved
        notify.send(
            sender=request.user,
            recipient=comment.author,
            verb=f'Your comment on "{comment.recipe.title}" was approved!',
            target=comment
        )

    return HttpResponseRedirect(reverse('comment_review'))


@staff_member_required
def comment_reject(request, pk):
    """Reject a comment"""
    if request.method == "POST":
        comment = get_object_or_404(Comment, pk=pk)
        # comment.status = Comment.Status.REJECTED
        # comment.save()
        messages.add_message(
            request, messages.SUCCESS,
            f'Comment by {comment.author} rejected.'
        )

        # USER STORY ACTION: Notify author when their comment is rejected
        notify.send(
            sender=request.user,
            recipient=comment.author,
            verb=f'Your comment on "{comment.recipe.title}" was rejected.',
            target=comment
        )

    return HttpResponseRedirect(reverse('comment_review'))
