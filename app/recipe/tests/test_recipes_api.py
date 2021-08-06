import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    """Creates and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Salt"):
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **kwargs):
    """Creates and returns a sample recipe"""

    defaults = {
        'title':  "Sample delicious recipe",
        'time_minutes': 10,
        'price': 50.00
    }

    defaults.update(kwargs)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests(TestCase):
    """Tests the public endpoints available under recipes API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """should not allow to access the endpoint unauthenticated"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Tests the authenticated endpoints available under recipes API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@mail.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """should correctly retrieve a list of recipes"""

        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """should retrieve a list of recipes from a specific user"""

        user2 = get_user_model().objects.create_user(
            "other@mail.com",
            "otherpass"
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """should retrieve a recipe detail view"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """should create a basic recipe"""
        payload = {
            "title": "Chocolate brigadeiro",
            "time_minutes": 30,
            "price": 15.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """should create a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Sweet')
        tag2 = sample_tag(user=self.user, name='Sour')
        payload = {
            "title": "Thai Chicken",
            "tags": [tag1.id, tag2.id],
            "time_minutes": 60,
            "price": 25.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """should create a recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='Milk')
        ingredient2 = sample_ingredient(user=self.user, name='Strawberry')
        payload = {
            "title": "Strawberry Icecream",
            "ingredients": [ingredient1.id, ingredient2.id],
            "time_minutes": 120,
            "price": 20.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_filter_recipes_by_tags(self):
        """should return recipes with given tags"""
        recipe1 = sample_recipe(user=self.user, title="Chicken Curry")
        recipe2 = sample_recipe(user=self.user, title="Lasagna")

        tag1 = sample_tag(user=self.user, name="Thai")
        tag2 = sample_tag(user=self.user, name="Italian")

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        recipe3 = sample_recipe(user=self.user, title="Fish and chips")

        res = self.client.get(
            RECIPES_URL,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """should return recipes with given ingredients"""
        recipe1 = sample_recipe(user=self.user, title="Chicken Curry")
        recipe2 = sample_recipe(user=self.user, title="Lasagna")

        ingredient1 = sample_ingredient(user=self.user, name="Curry")
        ingredient2 = sample_ingredient(user=self.user, name="Mozzarella")

        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        recipe3 = sample_recipe(user=self.user, title="Fish and chips")

        res = self.client.get(
            RECIPES_URL,
            {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)


class RecipeImageUploadTests(TestCase):
    """Tests image uploading for recipes API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@mail.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """should correctly upload an image to a recipe"""
        url = image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpeg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)

            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """should fail for a bad image request"""

        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': "notimage"}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
