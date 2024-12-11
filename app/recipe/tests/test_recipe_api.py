"""Test for recipe APIs."""

from decimal import Decimal
import tempfile
import os
from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse("recipe:recipe-list")


def create_ingredient(user, name="Sample Ingredient"):
    """Helper function to create and return an ingredient."""
    return Ingredient.objects.create(user=user, name=name)


def create_tag(user, name="Sample Tag"):
    """Helper function to create and return a tag."""
    return Tag.objects.create(user=user, name=name)


def detail_url(recipe_id):
    """Create and return en image upload URL."""
    return reverse("recipe:recipe-detail", args=[recipe_id])


def image_upload_url(recipe_id):
    """Helper function to create and return an image upload URL."""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


def create_recipe(user, num=1, **params):
    """Create and return a sample recipe."""
    defaults = {
        "title": "Sample recipe title",
        "time_minutes": 22,
        "price": Decimal("5.25"),
        "description": "Sample description",
        "link": "http://example.com/recipe.pdf",
    }

    tags = params.pop("tags", [])
    ingredients = params.pop("ingredients", [])
    defaults.update(params)

    recipes = []
    for _ in range(num):
        recipe = Recipe.objects.create(user=user, **defaults)

        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(user=user, **tag)
            recipe.tags.add(tag_obj)

        for ingredient in ingredients:
            ingredient_obj, _ = Ingredient.objects.get_or_create(user=user,
                                                                 **ingredient)
            recipe.ingredients.add(ingredient_obj)

        recipes.append(recipe)

    return recipes if num > 1 else recipes[0]


class PublicRecipeAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="test123", name="Test User")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user, num=2)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            email="other_user@example.com",
            password="test123",
            name="Other User")
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            # "user": self.user.id,
            "title": "Sample recipe",
            "time_minutes": 30,
            "price": Decimal("5.50"),
            "link": "http://example.com/recipe",
            "description": "Samle recipe",
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

        res = self.client.post(RECIPES_URL, payload, format="json")
        print("Response data:", res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        print(res.status_code)
        recipe = Recipe.objects.get(id=res.data["id"])

        tags = recipe.tags.values_list("name", flat=True)
        ingredients = recipe.ingredients.values_list("name", flat=True)
        self.assertCountEqual(tags, ["Vegan", "Dessert"])
        self.assertCountEqual(ingredients, ["Sugar", "Flour"])

    def test_partial_update(self):
        """Test partial update of a recipe."""
        recipe = create_recipe(
            user=self.user,
            title="Sample recipe title",
            link="http://example.com/recipe.pdf",
        )

        payload = {"title": "New recipe title"}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, "http://example.com/recipe.pdf")

    def test_delete_recipe(self):
        """Test deleting a recipe."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_ingredient_on_update(self):
        """Test creating an ingredient when updating a recipe."""
        recipe = create_recipe(user=self.user)

        payload = {"ingredients": [{"name": "Limes"}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(name="Limes")
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient when updating a recipe."""
        ingredient1 = Ingredient.objects.create(user=self.user, name="Pepper")
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(user=self.user, name="Salt")

        payload = {"ingredients": [{"name": "Salt"}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_create_recipe_with_ingredients_and_tags(self):
        """Test creating a recipe with ingredients and tags."""
        ingredient = create_ingredient(user=self.user, name="Cabbab")
        tag = create_tag(user=self.user, name="Meetlover")

        recipe = create_recipe(user=self.user,
                               title="Curry",
                               time_minutes=30,
                               price=Decimal("2.50"))
        recipe.ingredients.add(ingredient)
        recipe.tags.add(tag)

        self.assertEqual(recipe.title, "Curry")
        self.assertIn(ingredient, recipe.ingredients.all())
        self.assertIn(tag, recipe.tags.all())

    def test_cleare_recipe_ingredients(self):
        """Test clearing a recipes ingredients."""
        ingredient = Ingredient.objects.create(user=self.user, name="Garlic")
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {"ingredients": []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """Test filtering the recipe by tags."""
        r1 = create_recipe(user=self.user, title="Tai Vegetable Curry")
        r2 = create_recipe(user=self.user, title="Aubergine With Tahini")
        tag1 = Tag.objects.create(user=self.user, name="Vegan")
        tag2 = Tag.objects.create(user=self.user, name="Vegetarian")
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_recipe(user=self.user, title="Fish and Chips")

        params = {"tags": f"{tag1.id}, {tag2.id}"}
        res = self.client.get(RECIPES_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)
        print(res.data)

    def test_filter_by_ingredients(self):
        """Test for filtering recipes by ingredients."""
        r1 = create_recipe(user=self.user, title="Pasta")
        r2 = create_recipe(user=self.user, title="Salad")
        in1 = Ingredient.objects.create(user=self.user, name="Chicken")
        in2 = Ingredient.objects.create(user=self.user, name="Beef")
        r1.ingredients.add(in1)
        r2.ingredients.add(in2)
        r3 = create_recipe(user=self.user, title="Mixedmeet")

        params = {"ingredients": f"{in1.id},{in2.id}"}
        res = self.client.get(RECIPES_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)
        print(res.data)


class ImageUploadTests(TestCase):
    """Tests for the image upload API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@example.com", "password123")
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a recipe."""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(
                suffix=".jpg"
        ) as image_file:  # Helper module, temporery image file
            img = Image.new(
                "RGB",
                (10, 10))  # RMG -Library to store the image, tempoerery file
            img.save(image_file, format="JPEG")
            # Returning to the start of file, default after .save
            image_file.seek(0)
            payload = {"image": image_file}
            res = self.client.post(url, payload, format="multipart")

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_to_db(self):
        """Test uploading invalide image."""
        recipe = create_recipe(user=self.user)

        url = image_upload_url(recipe.id)

        res = self.client.post(url, {}, format="multipart")
        print("Res.data:", res.data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)

    @patch("core.models.Recipe")
    def test_image_upload_no_image(self, MockRecipe):
        """Test uploading no image."""
        # MockRecipe.objects.create = Mock(return_value=Mock(id=1))

        recipe = create_recipe(user=self.user)
        url = reverse("recipe:recipe-upload-image", args=[recipe.id])

        payload = {}
        res = self.client.post(url, payload, format="multipart")
        print("Res.data:", res.data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)
