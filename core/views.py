from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, RecipeForm
from django.core.paginator import Paginator
from .models import Recipe


def index(request):
    """Home page: show approved recipes as cards, 6 per page."""
    recipes = (
        Recipe.objects.filter(status=Recipe.Status.APPROVED)
        .select_related("author")
        .order_by("-created_at")
    )
    paginator = Paginator(recipes, 6)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "core/index.html",
        {"page_obj": page_obj},
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
