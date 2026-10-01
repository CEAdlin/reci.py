from django import forms
from .models import Comment, Recipe


class ProfileForm(forms.Form):
    """
    Form for editing ones email address on the profile page
    """
    email = forms.EmailField()


class RecipeForm(forms.ModelForm):
    category = forms.ChoiceField(
        choices=Recipe.Category.choices,
        required=False,
    )

    class Meta:
        model = Recipe
        fields = [
            "title",
            "image",
            "image_url",
            "description",
            "category",
            "ingredients",
            "method",
            "servings",
            "prep_time",
            "cook_time",
            "difficulty",
        ]
        labels = {
            "title": "Recipe title",
            "image": "Upload recipe image (optional)",
            "image_url": "Recipe image URL (optional fallback)",
            "description": "Short description",
            "ingredients": "Ingredients",
            "method": "Method",
            "servings": "Servings",
            "difficulty": "Difficulty",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "category": forms.Select(),
            "ingredients": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": "List one ingredient per line"
                }
            ),
            "method": forms.Textarea(attrs={"rows": 8}),
            "servings": forms.NumberInput(attrs={"min": 1}),
            "prep_time": forms.NumberInput(attrs={"min": 1}),
            "cook_time": forms.NumberInput(attrs={"min": 1}),
        }

    def clean_category(self):
        return self.cleaned_data.get("category") or Recipe.Category.OTHER


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Write a comment...",
                    "aria-label": "Comment text",
                }
            ),
        }
        labels = {
            "body": "",
        }

    def clean_body(self):
        body = self.cleaned_data.get("body", "").strip()
        if not body:
            raise forms.ValidationError("Comment cannot be empty.")
        return body
