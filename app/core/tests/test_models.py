"""
Test for models
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from core import models
from rest_framework.test import APIClient
from unittest.mock import patch

from rest_framework import status

RECIPES_URL = reverse("recipe:recipe-list")


def create_user(email="user@example.com", password="testpassword123"):
    """Create and returne a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test model"""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = "test@example.com"
        password = "testpass123"
        name = "Test User"
        user = get_user_model().objects.create_user(email=email,
                                                    password=password,
                                                    name=name)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.com", "test4@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            email="superuser@example.com",
            password="supertest123",
            name="Super User")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(email="test@example.com",
                                                    password="testpass123",
                                                    name="Test User")

        # Ensure the user is created and exists
        self.assertTrue(
            get_user_model().objects.filter(email="test@example.com").exists())

        # Log in the user
        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            "title": "Recipes",
            "time_minutes": 5,
            "price": Decimal("5.50"),
            "description": "Sample recipe description.",
            "link": "http://example.com/recipe/",
            "tags": [{
                "name": "Vegan"
            }, {
                "name": "Dessert"
            }],
            "ingredients": [{
                "name": "Sugar"
            }, {
                "name": "Flour"
            }],
        }

        res = client.post(RECIPES_URL, payload, format="json")
        print("Res data:", res.data)

        # Check if the response status code is 201
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Check if the recipe was created
        self.assertTrue(models.Recipe.objects.filter(title="Recipes").exists())

        recipe = models.Recipe.objects.get(title="Recipes")

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag1")

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient is successful."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name="Ingredient",
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch("core.models.uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = "test-uuid"  # Modify unic identifyer uuid to some degree
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, "example.jpg")

        self.assertEqual(
            file_path, f"uploads/recipe/{uuid}.jpg"
        )  # Checking that uuid replaces the name exmple.com with uuid
