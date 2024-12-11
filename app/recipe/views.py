"""
Views for the RecipeApi.
"""

from rest_framework import viewsets, mixins

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


@extend_schema_view(list=extend_schema(parameters=[
    OpenApiParameter(
        "tags",
        OpenApiTypes.STR,
        description="Comma separated list of IDs to filter.",
    ),
    OpenApiParameter(
        "ingredients",
        OpenApiTypes.STR,
        description="Comma separated list of IDs filter.",
    ),
]))
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API."""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrive recipes for authenticated user."""
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(
            user=self.request.user).order_by("-id").distinct()

    def get_serializer_class(self):
        """Return the serializer class for the request."""
        if self.action == "list":
            return serializers.RecipeSerializer
        elif self.action == "retrieve":
            return serializers.RecipeDetailSerializer
        elif self.action == "upload_image":
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe with nested tags and ingredients."""
        tags_data = self.request.data.get("tags", [])
        ingredients_data = self.request.data.get("ingredients", [])

        if not isinstance(tags_data, list) or not all(
                isinstance(tag, dict) and "name" in tag for tag in tags_data):
            raise ValidationError({
                "tags":
                "Tags must be a list of dictionaries with a 'name' key."
            })

        if not isinstance(ingredients_data, list) or not all(
                isinstance(ingredient, dict) and "name" in ingredient
                for ingredient in ingredients_data):
            raise ValidationError({
                "ingredients":
                "Ingredients must be a list of dictionaries with a 'name' key."
            })

        recipe = serializer.save(user=self.request.user)

        tags = []
        for tag in tags_data:
            if isinstance(tag, dict) and "name" in tag:
                tag_obj, _ = Tag.objects.get_or_create(user=self.request.user,
                                                       name=tag["name"])
                tags.append(tag_obj)

        ingredients = []
        for ingredient in ingredients_data:
            if isinstance(ingredient, dict) and "name" in ingredient:
                ingredient_obj, _ = Ingredient.objects.get_or_create(
                    user=self.request.user, name=ingredient["name"])
                ingredients.append(ingredient_obj)

        recipe.tags.set(tags)
        recipe.ingredients.set(ingredients)

        print("Saved Recipe ID:", recipe.id)

    @action(methods=["POST"], detail=True, url_path="upload_image")
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()

        if "image" not in request.data:
            return Response({"error": "No image provided"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(recipe,
                                         data=request.data,
                                         partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """Create a new recipe."""
        # Check if the recipe data is valid
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.errors)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        """Update the recipe, ensuring the current user is linked."""
        instance = serializer.save(user=self.request.user)
        return instance


@extend_schema_view(list=extend_schema(parameters=[
    OpenApiParameter(
        "assigned_only",
        OpenApiTypes.INT,
        enum=[0, 1],
        description="Filter by itemd assigned to recipes.",
    )
]))
class BaseRecipeAttrViewSet(
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet,
):
    """Base viewset or recipe attribute."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticate user."""
        assigned_only = bool(
            int(self.request.query_params.get("assigned_only", 0)))
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user).order_by("-name").distinct()


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients inthe database."""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
