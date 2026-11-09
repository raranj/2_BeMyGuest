from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from .forms import UserForm
from .models import Allergy, User


@login_required
@require_http_methods(["GET", "POST"])
def user_page(request):
    """View, create, or update only the signed-in account's profile."""
    profile = User.objects.filter(account=request.user).first()
    initial = {"name": request.user.get_full_name() or request.user.get_username(), "email": request.user.email}
    form = UserForm(request.POST if request.method == "POST" else None, instance=profile, initial=initial if profile is None else None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            profile = form.save(commit=False)
            profile.account = request.user
            profile.save()
            form.save_m2m()
        messages.success(request, "Your profile has been saved.")
        return redirect("users:user")
    editing = request.method == "POST" or request.GET.get("edit") == "1"
    return render(request, "users/user.html", {"form": form, "profile": profile, "editing": editing})


@login_required
@require_http_methods(["GET"])
def allergy_suggestions(request):
    query = " ".join(request.GET.get("q", "").split()).casefold()[:100]
    terms = Allergy.objects.filter(name__icontains=query) if query else Allergy.objects.none()
    return JsonResponse({"results": list(terms.values_list("name", flat=True)[:20])})
