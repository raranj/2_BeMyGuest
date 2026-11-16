import math
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


def validate_string_list(value):
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValidationError("Enter a list of nonempty strings.")


def validate_score(value):
    if not math.isfinite(value):
        raise ValidationError("Enter a finite rating between 1 and 5.")


class DietaryPreference(models.TextChoices):
    OMNIVORE = "omnivore", "Omnivore / Regular Diet (Eats everything, no restrictions on meat, seafood, dairy, or plants)"
    VEGETARIAN = "vegetarian", "Vegetarian (No meat, poultry, or seafood; eats dairy and eggs)"
    VEGAN = "vegan", "Vegan (No meat, poultry, seafood, dairy, eggs, or any animal-derived ingredients like honey)"
    PESCATARIAN = "pescatarian", "Pescatarian (No meat or poultry; eats fish, seafood, and plant-based foods)"
    FLEXITARIAN = "flexitarian", "Flexitarian (Primarily plant-based diet, but occasionally eats meat or seafood)"
    KETO = "keto", "Low-Carb / Keto (Very low carbohydrate intake; high fat and moderate protein from meat, fish, and oils)"
    PALEO = "paleo", "Paleo (No grains, legumes, dairy, or processed foods; eats lean meats, fish, fruits, and vegetables)"
    MEDITERRANEAN = "mediterranean", "Mediterranean (High intake of vegetables, whole grains, beans, fish, and olive oil; low intake of red meat)"
    HALAL = "halal", "Halal (No pork, alcohol, or meat from animals not slaughtered according to Islamic law)"
    KOSHER = "kosher", "Kosher (No pork or shellfish; meat and dairy must never be prepared or consumed together)"
    OTHERS = "others", "Others"


class Allergy(models.Model):
    """Shared, case-insensitive vocabulary for allergy matching across features."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        self.name = " ".join(self.name.split()).casefold()
        self.full_clean(validate_unique=False)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class User(models.Model):
    """Meal-sharing profile; credentials stay in Django's authentication model."""
    id = models.BigAutoField(primary_key=True)
    account = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="meal_profile")
    name = models.CharField(max_length=150)
    email = models.EmailField()
    dietary_preferences = models.CharField(max_length=20, choices=DietaryPreference.choices, default=DietaryPreference.OTHERS, verbose_name="dietary preference")
    allergies = models.ManyToManyField(Allergy, blank=True, related_name="profiles")
    created_at = models.DateTimeField(auto_now_add=True)
    host_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5), validate_score])
    guest_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5), validate_score])

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(dietary_preferences__in=DietaryPreference.values), name="users_dietary_preference_valid"),
            models.CheckConstraint(condition=models.Q(host_score__isnull=True) | models.Q(host_score__gte=1, host_score__lte=5), name="users_host_score_range"),
            models.CheckConstraint(condition=models.Q(guest_score__isnull=True) | models.Q(guest_score__gte=1, guest_score__lte=5), name="users_guest_score_range"),
        ]

    def __str__(self):
        return self.name
