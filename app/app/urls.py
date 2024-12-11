"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.contrib import admin
from django.urls import path, include
from user.views import APIRootView
from rest_framework.routers import DefaultRouter
from user import views as user_views
from recipe import views as recipe_views
from django.conf.urls.static import static
from django.conf import settings

app_name = "api"

router = DefaultRouter()
router.register(r"users", user_views.UserViewSet, basename="user")
router.register(r"recipes", recipe_views.RecipeViewSet, basename="recipe")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", APIRootView.as_view(), name="api_root"),
    path("api/schema/", SpectacularAPIView.as_view(), name="api_schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api_schema"),
        name="api_docs",
    ),
    path("api/user/", include("user.urls")),
    path("api/recipe/", include("recipe.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
