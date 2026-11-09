from django import forms
from .models import Allergy, User


class CommaSeparatedListField(forms.CharField):
    def prepare_value(self, value):
        if isinstance(value, list) and value and isinstance(value[0], Allergy):
            value = [term.name for term in value]
        return ", ".join(value) if isinstance(value, list) else value

    def clean(self, value):
        value = super().clean(value)
        terms = list(dict.fromkeys(" ".join(item.split()).casefold() for item in value.split(",") if item.strip())) if value else []
        if any(len(term) > 100 for term in terms):
            raise forms.ValidationError("Each allergy must be 100 characters or fewer.")
        return terms


class UserForm(forms.ModelForm):
    allergies = CommaSeparatedListField(required=False, help_text="Type to find an existing allergy, then press Enter to add it or a new term. Remove a term with its × button. Without JavaScript, separate terms with commas.")

    def _save_m2m(self):
        terms = [Allergy.objects.get_or_create(name=name)[0] for name in self.cleaned_data["allergies"]]
        self.instance.allergies.set(terms)

    class Meta:
        model = User
        fields = ["name", "email", "dietary_preferences", "allergies"]
