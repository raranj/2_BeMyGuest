from django.contrib import admin
from .models import Recipe

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe_name', 'creator', 'difficulty', 'created_at')
    search_fields = ('recipe_name', 'description')
    list_filter = ('difficulty', 'created_at')