from django.conf import settings
from django.db import models


class Recipe(models.Model):
    # Difficulty options matching the chart
    class Difficulty(models.TextChoices):
        EASY = 'Easy', 'Easy'
        MEDIUM = 'Medium', 'Medium'
        HARD = 'Hard', 'Hard'

    # id: BigAutoField (PK)
    id = models.BigAutoField(primary_key=True)

    # creator_id: ForeignKey (FK)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='User who created recipe',
    )

    # recipe_name: CharField
    recipe_name = models.CharField(max_length=255)

    # description: TextField
    description = models.TextField(
        blank=True,
        help_text='Recipe introduction, story behind this recipe',
    )

    # ingredients: JSONField
    ingredients = models.JSONField(
        default=list, help_text='Ingredient names and quantities'
    )

    # instructions: JSONField
    instructions = models.JSONField(
        default=list, help_text='Ordered cooking steps'
    )

    # preparation_time: IntegerField
    preparation_time = models.IntegerField(
        default=0, help_text='Preparation time (minutes)'
    )

    # cooking_time: IntegerField
    cooking_time = models.IntegerField(
        default=0, help_text='Cooking time (minutes)'
    )

    # servings: PositiveIntegerField
    servings = models.PositiveIntegerField(
        default=1, help_text='Number of servings'
    )

    # difficulty: CharField
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
    )

    # dietary_tags: JSONField
    dietary_tags = models.JSONField(
        default=list, blank=True, help_text='Vegetarian, vegan, etc.'
    )

    # allergens: JSONField
    allergens = models.JSONField(
        default=list, blank=True, help_text='Peanut, milk, eggs, etc.'
    )

    # image: ImageField
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)

    # created_at: DateTimeField
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.recipe_name