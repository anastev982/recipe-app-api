"""Serializers for the user API view."""

from rest_framework import serializers
from core.models import Recipe
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for listing recipes."""

    class Meta:
        model = Recipe
        fields = ["id", "title", "description", "user"]


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Serializer for recipe detail view."""

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "description",
            "ingredients",
            "instructions",
            "user"]


class APIRootSerializer(serializers.Serializer):
    schema = serializers.CharField()
    docs = serializers.CharField()
    user = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Serializers for the user object."""

    class Meta:
        model = get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        user = get_user_model().objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        """Validate and authenticate user."""
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
