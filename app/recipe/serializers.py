#
"""Serializers foe recipe APIs."""

from rest_framework import serializers
from core.models import Ingredient  # Ensure the import is not missing

from core.models import (
    Tag,
    Recipe,
)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer fro ingredients."""

    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if not attrs.get("name"):
            raise serializers.ValidationError("Tag name is required.")
        return attrs


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)
    image = serializers.ImageField(required=False, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "title",
            "time_minutes",
            "price",
            "link",
            "tags",
            "ingredients",
            "description",
            "image",
        )
        extra_kwargs = {"image": {"required": False, "allow_null": True}}
        read_only_fields = ["id"]

        def validat_image(self, value):
            if value is None:
                return value
            return value

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting ot creating tags as needed."""
        auth_user = self.context["request"].user
        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
                # name=tag['name']
            )

            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context["request"].user
        for ingredient in ingredients:
            ingredient_obj, _ = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
                # name=ingredient['name']
            )

            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a recipe."""
        tags_data = validated_data.pop("tags", [])
        ingredients_data = validated_data.pop("ingredients", [])
        image = validated_data.pop("image", None)
        recipe = Recipe.objects.create(**validated_data)

        self._get_or_create_tags(tags_data, recipe)
        self._get_or_create_ingredients(ingredients_data, recipe)

        if image:
            recipe.image = image
            recipe.save()

        return recipe

    def update(self, instance, validated_data):
        """Update a recipe."""
        tags_data = validated_data.pop("tags", None)
        ingredients_data = validated_data.pop("ingredients", None)

        instance = super().update(instance, validated_data)

        if tags_data is not None:
            instance.tags.clear()
            instance.save()
            self._get_or_create_tags(tags_data, instance)

        if ingredients_data is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients_data, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    description = serializers.CharField()
    image = serializers.ImageField(required=False)

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ("description", "image")


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": False, "allow_null": True}}
