from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import User
import logging

logger = logging.getLogger(__name__)


class UserAPITests(APITestCase):

    def setUp(self):
        """Create a test user before each test."""
        self.user_url = reverse("user:user-list")
        self.user_data = {
            "email": "testuser@example.com",
            "password": "testpassword",
            "name": "Test User",
        }
        self.user = User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            name=self.user_data["name"],
        )

    def test_create_user(self):
        """Test the user creation endpoint and token generation."""

        data = {
            "email": "newuser@example.com",
            "password": "testpassword",  # Adjust as necessary
            "name": "New User",
        }

        # Make the POST request to create a new user
        response = self.client.post(self.user_url, data)
        print("Response Data:", response.data)

        logger.debug(f"Create User Response: {response.data}")

        # Assert that the response status is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        logger.debug(f"Create User Response Content: {response.content}")

        # Verify the user has been created
        user_exists = User.objects.filter(email=data["email"]).exists()
        self.assertTrue(user_exists)

        # Optionally, check the response contains user data
        self.assertIn("email", response.data)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["email"], data["email"])
        self.assertEqual(response.data["name"], data["name"])

    def test_token_generation(self):
        """Test token generation for a created user."""

        # First, create the user to generate a token
        self.client.post(self.user_url, self.user_data)

        url = reverse("user:token")
        response = self.client.post(
            url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)  # Check for access token

    def test_create_token_bad_credentials(self):
        """Test return error if credentials are invalid."""
        # Create a user for testing
        User.objects.create_user(
            email="test@example.com", password="goodpass", name="Test User"
        )

        # Use invalid credentials
        response = self.client.post(
            reverse("user:token"),
            {"email": "test@example.com", "password": "badpass"},
        )

        logger.debug(f"Bad credentials Response: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
