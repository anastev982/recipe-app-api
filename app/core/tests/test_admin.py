"""Test for the Django admin modifications."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        """Create user and client."""
        User = get_user_model()
        self.client = Client()

        # Delete existing user.
        existing_user = User.objects.filter(email='admin@example.com').first()
        if existing_user:
            existing_user.delete()

        # Create a superuser (admin)
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='Ana',
            name='Test Admin'
        )

        # Create a regular user with a different email
        self.user = User.objects.create_user(
            email='user@example.com',
            password='Ana',
            name='Test User'
        )

        # Force login the admin
        self.client.force_login(self.admin)
        print(f"Admin logged in: {self.admin.email}")

    def test_login(self):
        """Test the login page."""
        url = reverse('admin:login')

        # Log out any existing user before accessing the login page
        self.client.logout()

        res = self.client.get(url)
        self.assertEqual(res.status_code, 200, "Login page should return 200 OK.")  # Check that the login page is loaded successfully.

        # Perform a login attempt
        res = self.client.post(url, {'username': 'admin@example.com', 'password': 'Ana'})
        
        # Check that it redirects to the admin page
        self.assertRedirects(res, reverse('admin:index'), msg_prefix="Should redirect to admin index after login.")

       
    def test_user_list(self):
        """Test the users are listed on the user change list page."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works."""
        self.client.force_login(self.admin)  # Ensure the admin is logged in before accessing the create user page

        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        print(f"Login page response status code: {res.status_code}")  # Should be 200 if the login is accessible

        # Debug information
        if res.status_code != 200:
            print(f"Redirected URL: {res.url}")  # Print the redirect URL if any
            print(f"Response content: {res.content}")  # Print the response content for further insights

        self.assertEqual(res.status_code, 200,"Create user page should return 200 OK.")

