from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ProfileForm, RecipeForm
from .models import Recipe


PUBLIC_RECIPE_STATUSES = [Recipe.Status.APPROVED, Recipe.Status.PUBLISHED]


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
            messages.success(
                request,
                "Your recipe has been submitted and is awaiting review.",
            )
            return redirect("index")
    else:
        form = RecipeForm()

    return render(request, "core/submit_recipe.html", {"form": form})
