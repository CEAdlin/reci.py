from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, RecipeForm
from .models import Recipe


def index(request):
    """View for the home page"""
    return render(
        request,
        "core/index.html",
    )


def recipe_detail(request, pk):
    """Display a recipe only after it has been published."""
    recipe = get_object_or_404(
        Recipe,
        pk=pk,
        status=Recipe.Status.PUBLISHED,
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
            messages.success(
                request,
                "Your recipe has been submitted and is awaiting review.",
            )
            return redirect("index")
    else:
        form = RecipeForm()

    return render(request, "core/submit_recipe.html", {"form": form})
