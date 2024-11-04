"""URL mapping for the recipe API."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipe import views

app_name = "recipe"

# Create a router and register the RecipeViewSet.
router = DefaultRouter()
router.register(r"recipes", views.RecipeViewSet, basename="recipe")

# Define the URL patterns
urlpatterns = [
    path("", include(router.urls)),  # Include router URLs
]
