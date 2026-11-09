from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from features.users.models import User
from features.recipes.models import Recipe
from .models import MealGathering


class MealGatheringForm(forms.ModelForm):

    date_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M"
        ),
        input_formats=["%Y-%m-%dT%H:%M"]
    )

    class Meta:
        model = MealGathering

        fields = [
            "title",
            "description",
            "cuisine_type",
            "date_time",
            "location",
            "max_guests",
            "meal_name",
            "meal_description",
            "meal_image",
            "recipe"
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "meal_description": forms.Textarea(attrs={"rows": 3})
        }

        labels = {
            "max_guests": "Maximum Guests",
            "location": "Approximate Location",
            "recipe": "Related Recipe"
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields["recipe"].queryset = Recipe.objects.filter(
                creator=user
            )

    def clean_date_time(self):
        date_time = self.cleaned_data["date_time"]

        if date_time <= timezone.now():
            raise forms.ValidationError(
                "Please choose a future date and time."
            )

        return date_time


def gathering_list(request):

    gatherings = MealGathering.objects.filter(
        status="open",
        date_time__gt=timezone.now()
    )

    search = request.GET.get("q", "").strip()

    if search:
        gatherings = gatherings.filter(
            Q(title__icontains=search) |
            Q(cuisine_type__icontains=search) |
            Q(meal_name__icontains=search) |
            Q(location__icontains=search)
        )

    gatherings = gatherings.order_by("date_time")

    context = {
        "gatherings": gatherings,
        "search": search
    }

    return render(request, "posts.html", context)


def gathering_detail(request, gathering_id):

    gathering = get_object_or_404(
        MealGathering,
        id=gathering_id
    )

    context = {
        "gathering": gathering
    }

    return render(request, "post_detail.html", context)


@login_required
def gathering_create(request):

    profile = User.objects.filter(
        account=request.user
    ).first()

    if profile is None:
        messages.error(
            request,
            "Please create your profile before hosting a meal."
        )
        return redirect("users:user")

    if request.method == "POST":

        form = MealGatheringForm(
            request.POST,
            request.FILES,
            user=request.user
        )

        if form.is_valid():

            gathering = form.save(commit=False)

            gathering.host = profile

            gathering.status = "open"

            gathering.save()

            messages.success(
                request,
                "Your meal gathering was created!"
            )

            return redirect(
                "gathering_detail",
                gathering_id=gathering.id
            )

    else:
        form = MealGatheringForm(user=request.user)

    context = {
        "form": form,
        "editing": False
    }

    return render(request, "post_form.html", context)


@login_required
def gathering_edit(request, gathering_id):

    gathering = get_object_or_404(
        MealGathering,
        id=gathering_id,
        host__account=request.user
    )

    if request.method == "POST":

        form = MealGatheringForm(
            request.POST,
            request.FILES,
            instance=gathering,
            user=request.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Your gathering was updated!"
            )

            return redirect(
                "gathering_detail",
                gathering_id=gathering.id
            )

    else:
        form = MealGatheringForm(
            instance=gathering,
            user=request.user
        )

    context = {
        "form": form,
        "editing": True,
        "gathering": gathering
    }

    return render(request, "post_form.html", context)


@login_required
@require_POST
def gathering_cancel(request, gathering_id):

    gathering = get_object_or_404(
        MealGathering,
        id=gathering_id,
        host__account=request.user
    )

    gathering.status = "cancelled"

    gathering.save()

    messages.success(
        request,
        "Your meal gathering was cancelled."
    )

    return redirect(
        "gathering_detail",
        gathering_id=gathering.id
    )


@login_required
def my_gatherings(request):

    gatherings = MealGathering.objects.filter(
        host__account=request.user
    )

    gatherings = gatherings.order_by("-date_time")

    context = {
        "gatherings": gatherings,
        "mine": True
    }

    return render(request, "posts.html", context)
