from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import CommentForm, ProfileForm, RecipeForm
from .models import Comment, Recipe
from notifications.signals import notify


def index(request):
    """Show public recipes with sorting and filtering controls."""
    recipes = (
        Recipe.objects.filter(
            status__in=[Recipe.Status.APPROVED, Recipe.Status.PUBLISHED]
        )
        .select_related("author")
        .annotate(like_count=Count("liked_by", distinct=True))
    )

    name = request.GET.get("name", "").strip()
    category = request.GET.get("category", "")
    difficulty = request.GET.get("difficulty", "")
    sort = request.GET.get("sort", "date")
    liked = request.GET.get("liked") == "1"

    if name:
        recipes = recipes.filter(title__icontains=name)
    if category in dict(Recipe.Category.choices):
        recipes = recipes.filter(category=category)
    if difficulty in dict(Recipe.Difficulty.choices):
        recipes = recipes.filter(difficulty=difficulty)
    if liked and request.user.is_authenticated:
        recipes = recipes.filter(liked_by=request.user)

    sort_fields = {
        "name": "title",
        "date": "-created_at",
        "likes": "-like_count",
    }
    recipes = recipes.order_by(sort_fields.get(sort, "-created_at"), "title")

    paginator = Paginator(recipes, 6)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)
    return render(
        request,
        "core/index.html",
        {
            "page_obj": page_obj,
            "categories": Recipe.Category.choices,
            "difficulties": Recipe.Difficulty.choices,
            "selected_name": name,
            "selected_category": category,
            "selected_difficulty": difficulty,
            "selected_sort": sort if sort in sort_fields else "date",
            "liked_only": liked and request.user.is_authenticated,
            "query_string": query_params.urlencode(),
        },
    )


@login_required
def toggle_recipe_like(request, pk):
    """Toggle the current user's like and return to the recipe list."""
    if request.method != "POST":
        raise ValidationError("Likes must be changed with POST.")

    recipe = get_object_or_404(
        Recipe,
        pk=pk,
        status__in=[Recipe.Status.APPROVED, Recipe.Status.PUBLISHED],
    )
    if recipe.liked_by.filter(pk=request.user.pk).exists():
        recipe.liked_by.remove(request.user)
    else:
        recipe.liked_by.add(request.user)

    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse("index")
    return redirect(next_url)


@login_required
def profile(request):
    """
    View for the profile page.

    Displays the logged-in user's username and published recipes.
    Allows the user to update their own email address with validation.
    """
    if request.method == "POST":
        form = ProfileForm(data=request.POST)
        if form.is_valid():
            request.user.email = form.cleaned_data["email"]
            request.user.save()
            messages.add_message(
                request, messages.SUCCESS,
                f'Email address changed to {request.user.email}'
            )
            return redirect("profile")

    else:
        form = ProfileForm(initial={"email": request.user.email})

    # Fetch only published recipes belonging to the currently logged-in user
    user_recipes = Recipe.objects.filter(
        author=request.user,
        status__in=[
            Recipe.Status.APPROVED,
            Recipe.Status.PUBLISHED,
        ],
    ).order_by("-created_at")

    return render(
        request,
        "core/profile.html",
        {
            "form": form,
            "user_recipes": user_recipes,
        }
    )


@login_required
def submit_recipe(request):
    """Allow authenticated users to submit a recipe for review."""
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.status = recipe.Status.PENDING
            recipe.save()
            notify.send(
                sender=request.user,
                recipient=request.user,
                verb=f'Your recipe "{recipe.title}" was submitted '
                     'and is pending review.',
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
# MY RECIPES: EDIT AND DELETE (USER STORY #9)
# ==========================================


def get_own_recipe(request, pk):
    """
    Return the recipe with this pk if the logged-in user wrote it.
    Anyone else gets a 403 Forbidden page.
    """
    recipe = get_object_or_404(Recipe, pk=pk)
    if recipe.author != request.user:
        raise PermissionDenied
    return recipe


@login_required
def my_recipes(request):
    """List every recipe the logged-in user has written, with its status."""
    recipes = \
        Recipe.objects.filter(author=request.user).order_by("-created_at")
    return render(request, "core/my_recipes.html", {"recipes": recipes})


@login_required
def edit_recipe(request, pk):
    """
    Let an author edit their own recipe.
    Edited recipes go back to pending so an admin can check them again.
    """
    recipe = get_own_recipe(request, pk)

    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            recipe = form.save(commit=False)
            was_public = recipe.status in [
                Recipe.Status.APPROVED, Recipe.Status.PUBLISHED
            ]
            recipe.status = Recipe.Status.PENDING
            recipe.save()
            if was_public:
                message = (
                    f'"{recipe.title}" was updated and is back in the '
                    "review queue. It will reappear once it is approved."
                )
            else:
                message = \
                    f'"{recipe.title}" was updated and is awaiting review.'
            messages.success(request, message)
            notify.send(
                sender=request.user,
                recipient=request.user,
                verb=f'Your recipe "{recipe.title}" '
                     f'was edited and is pending review.',
                target=recipe
            )
            return redirect("my_recipes")
        messages.error(request, "Please correct the errors below.")
    else:
        form = RecipeForm(instance=recipe)

    return render(
        request,
        "core/edit_recipe.html",
        {"form": form, "recipe": recipe},
    )


@login_required
def delete_recipe(request, pk):
    """
    Ask the author to confirm, then delete their recipe.
    GET shows the confirmation page; only POST deletes.
    """
    recipe = get_own_recipe(request, pk)

    if request.method == "POST":
        title = recipe.title
        recipe.delete()
        messages.success(request, f'"{title}" was deleted.')
        return redirect("my_recipes")

    return render(request, "core/delete_recipe.html", {"recipe": recipe})


# ==========================================
# NOTIFICATIONS SYSTEM VIEWS
# ==========================================

@login_required
def notifications_inbox(request):
    """
    Fulfill Acceptance Criteria: Lists messages and handles marking
    notifications as read.
    """
    # If user clicks "Mark as read", process the request
    notification_id = request.GET.get('mark_read')
    if notification_id:
        notification = get_object_or_404(
            request.user.notifications.unread(),
            id=notification_id
        )
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


def get_recipe_detail_context(user, recipe):
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
    comments = recipe.comments.order_by("-created_at")
    if not user.is_staff:
        comments = \
            comments.filter(approved=True) | comments.filter(author=user.id)

    return {
        "recipe": recipe,
        "ingredients": ingredients,
        "method_steps": method_steps,
        "comments": comments,
        "comment_form": CommentForm(),
    }


def recipe_detail(request, pk):
    """Display recipe details and handle new comment submission."""
    recipe = get_object_or_404(
        Recipe,
        pk=pk,
        status__in=[Recipe.Status.APPROVED, Recipe.Status.PUBLISHED],
    )
    context = get_recipe_detail_context(request.user, recipe)
    comment_form = context["comment_form"]

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(
                request,
                "You must be logged in to leave a comment."
            )
            return redirect("recipe_detail", pk=pk)

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.recipe = recipe
            comment.save()

            # USER STORY ACTION: Notify the recipe author
            # when someone comments on it
            if recipe.author != request.user:
                notify.send(
                    sender=request.user,
                    recipient=recipe.author,
                    verb=f'{request.user.username} commented '
                         f'on your recipe "{recipe.title}".',
                    target=recipe
                )

            messages.success(request, "Comment submitted successfully!")
            return redirect("recipe_detail", pk=pk)
        else:
            messages.error(
                request,
                "Error submitting comment. Please try again."
            )

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
        Comment.objects.filter(approved=False).first()

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
        context = get_recipe_detail_context(request.user, pending)
        context["approval"] = True
        return render(request, "core/recipe_detail.html", context)


@staff_member_required
def comment_review(request):
    """
    Allow the admin to approve or deny comments.
    Each time this is called it shows a recipe with a pending comment.
    """
    pending = Comment.objects.filter(approved=False).first()
    if pending is None:
        return HttpResponseRedirect(reverse('recipe_admin'))
    else:
        context = get_recipe_detail_context(request.user, pending.recipe)
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
        comment.approved = True
        comment.save()
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
        comment.delete()
        messages.add_message(
            request, messages.SUCCESS,
            f'Comment by {comment.author} rejected.'
        )

        # USER STORY ACTION: Notify author when their comment is rejected
        notify.send(
            sender=request.user,
            recipient=comment.author,
            verb=f'Your comment on "{comment.recipe.title}" was rejected.',
        )

    return HttpResponseRedirect(reverse('comment_review'))
