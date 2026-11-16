from django.urls import path
from .views import allergy_suggestions, user_page

app_name = "users"
urlpatterns = [
    path("", user_page, name="user"),
    path("allergies/", allergy_suggestions, name="allergy_suggestions"),
]
