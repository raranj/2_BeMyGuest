from django import forms
from .models import Recipe


class RecipeForm(forms.ModelForm):
    # Use clean TextAreas so users can enter items on new lines instead of raw JSON
    ingredients_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': '3 bananas\n180g cake flour\n2 eggs'}),
        label='Ingredients (one per line)',
        required=True
    )
    instructions_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5,
                                     'placeholder': 'Preheat oven to 356°F\nMix wet and dry ingredients\nBake for 40 minutes'}),
        label='Instructions (one step per line)',
        required=True
    )
    dietary_tags_text = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Vegetarian, Gluten-Free'}),
        label='Dietary Tags (comma-separated)',
        required=False
    )
    allergens_text = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Dairy, Eggs, Gluten'}),
        label='Allergens (comma-separated)',
        required=False
    )

    class Meta:
        model = Recipe
        fields = [
            'recipe_name',
            'description',
            'preparation_time',
            'cooking_time',
            'servings',
            'difficulty',
            'image',
        ]

    def clean(self):
        cleaned_data = super().clean()

        # Convert newline-separated text into JSON lists
        ing_text = cleaned_data.get('ingredients_text', '')
        cleaned_data['ingredients'] = [item.strip() for item in ing_text.splitlines() if item.strip()]

        inst_text = cleaned_data.get('instructions_text', '')
        cleaned_data['instructions'] = [step.strip() for step in inst_text.splitlines() if step.strip()]

        tags_text = cleaned_data.get('dietary_tags_text', '')
        cleaned_data['dietary_tags'] = [tag.strip() for tag in tags_text.split(',') if tag.strip()]

        allergens_text = cleaned_data.get('allergens_text', '')
        cleaned_data['allergens'] = [item.strip() for item in allergens_text.split(',') if item.strip()]

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.ingredients = self.cleaned_data['ingredients']
        instance.instructions = self.cleaned_data['instructions']
        instance.dietary_tags = self.cleaned_data['dietary_tags']
        instance.allergens = self.cleaned_data['allergens']
        if commit:
            instance.save()
        return instance