from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "host_score", "guest_score", "created_at")
    search_fields = ("name", "email")
    readonly_fields = ("created_at",)
