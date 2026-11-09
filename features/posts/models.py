from django.db import models
from django.core.validators import MinValueValidator


class MealGathering(models.Model):

    STATUS_CHOICES = [
        ("open", "Open"),
        ("full", "Full"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    id = models.BigAutoField(primary_key=True)

    host = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="meal_gatherings"
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    cuisine_type = models.CharField(max_length=100)

    date_time = models.DateTimeField()

    location = models.CharField(max_length=200)

    max_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    meal_name = models.CharField(
        max_length=200,
        blank=True
    )

    meal_description = models.TextField(blank=True)

    meal_image = models.ImageField(
        upload_to="meal_gatherings/",
        blank=True
    )

    recipe = models.ForeignKey(
        "recipes.Recipe",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meal_gatherings"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )

    def __str__(self):
        return self.title
