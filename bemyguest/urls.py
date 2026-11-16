"""
URL configuration for bemyguest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

"""
URL configuration for bemyguest project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView

from features.recipes import views as recipe_views
from features.posts import views as post_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include("features.users.urls")),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("recipes/", recipe_views.recipe_list, name="recipes"),
    path("recipes/create/", recipe_views.recipe_create, name="recipe_create"),
    path("recipes/<int:pk>/", recipe_views.recipe_detail, name="recipe_detail"),

    path("posts/", post_views.gathering_list, name="posts"),
    path("posts/create/", post_views.gathering_create, name="gathering_create"),
    path("posts/mine/", post_views.my_gatherings, name="my_gatherings"),
    path("posts/<int:gathering_id>/", post_views.gathering_detail, name="gathering_detail"),
    path("posts/<int:gathering_id>/edit/", post_views.gathering_edit, name="gathering_edit"),
    path("posts/<int:gathering_id>/cancel/", post_views.gathering_cancel, name="gathering_cancel"),
    path("invitations/", TemplateView.as_view(template_name="invitations.html"), name="invitations"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)