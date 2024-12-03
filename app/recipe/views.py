from rest_framework import viewsets, mixins

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API."""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrive recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class for the request."""
        if self.action == "list":
            return serializers.RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe with nested tags and ingredients."""
        tags_data = self.request.data.get('tags', [])
        ingredients_data = self.request.data.get('ingredients', [])

        tags = []
        for tag in tags_data:
            if isinstance(tag, dict) and 'name' in tag:
                tag_obj, _ = Tag.objects.get_or_create(
                    user=self.request.user,
                    name=tag['name']
                )
                tags.append(tag_obj)

        ingredients = []
        for ingredient in ingredients_data:
            if isinstance(ingredient, dict) and 'name' in ingredient:
                ingredient_obj, _ = Ingredient.objects.get_or_create(
                    user=self.request.user,
                    name=ingredient['name']
                )
                ingredients.append(ingredient_obj)

        recipe = serializer.save(user=self.request.user)
        recipe.tags.set(tags)
        recipe.ingredients.set(ingredients)

    def create(self, request, *args, **kwargs):
        """Create a new recipe."""
        # Check if the recipe data is valid
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        """Update the recipe, ensuring the current user is linked."""
        instance = serializer.save(user=self.request.user)
        return instance


class BaseRecipeAttrViewSet(mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset or recipe attribute."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticate user."""
        return self.queryset.filter(user=self.request.user).order_by("-name")


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
