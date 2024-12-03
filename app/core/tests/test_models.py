"""
Test for models
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from core import models
from rest_framework.test import APIClient


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
        user = get_user_model().objects.create_user(
            email=email, password=password, name=name
        )

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
            name="Super User"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            email="test@example.com", password="testpass123", name="Test User"
        )

        # Ensure the user is created and exists
        self.assertTrue(
            get_user_model().objects.filter(email="test@example.com").exists()
        )

        # Log in the user
        client = APIClient()
        client.force_authenticate(user=user)

        url = reverse("recipe:recipe-list")

        payload = {
            "title": "Recipes",
            "time_minutes": 5,
            "price": Decimal("5.50"),
            "description": "Sample recipe description.",
        }

        res = client.post(url, payload)

        # Check if the response status code is 201
        self.assertEqual(res.status_code, 201)
        print(res.data)  # This will show you the response data

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
