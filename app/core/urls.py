from recipe.views import RecipeViewSet
from rest_framework.routers import DefaultRouter
from user.views import UserViewSet
from django.urls import path, include

app_name = "core"

router = DefaultRouter()
router.register(r"recipes", RecipeViewSet, basename="recipe")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
