from django import forms
from .models import Comment, Recipe


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