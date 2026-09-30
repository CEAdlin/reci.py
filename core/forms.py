from django import forms
from .models import Recipe


class ProfileForm(forms.Form):
    """
    Form for editing ones email address on the profile page
    """
    email = forms.EmailField()


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "title",
            "image_url",
            "description",
            "ingredients",
            "method",
            "servings",
            "prep_time",
            "cook_time",
            "difficulty",
        ]
        labels = {
            "title": "Recipe title",
            "image_url": "Recipe image URL (optional)",
            "description": "Short description",
            "ingredients": "Ingredients",
            "method": "Method",
            "servings": "Servings",
            "difficulty": "Difficulty",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "ingredients": forms.Textarea(
                attrs={"rows": 6, "placeholder": "List one ingredient per line"}
            ),
            "method": forms.Textarea(attrs={"rows": 8}),
            "servings": forms.NumberInput(attrs={"min": 1}),
            "prep_time": forms.NumberInput(attrs={"min": 1}),
            "cook_time": forms.NumberInput(attrs={"min": 1}),
        }
