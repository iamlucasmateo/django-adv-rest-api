from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    return reverse(f'recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    """Create sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    """Create sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    default = {
        'title': 'Carrot Cake',
        'time_minutes': 32,
        'price': 10.00,
    }
    default.update(params)

    return Recipe.objects.create(user=user, **default)


class PublicRecipeAPITest(TestCase):
    """Test unauthenticated API function"""

    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        """Test auth is required"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITest(TestCase):
    """Test authenticated access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'pass123456'
        )
        self.client.force_authenticate(self.user)
    
    def test_retrieve_recipes(self):
        """Test recipes can be retrieved"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user, title='Kale Salad')

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        # many=True for a list view
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_recipes_limited_to_user(self):
        """Test recipes limited to user"""
        user2 = get_user_model().objects.create_user(
            'other@mail.com',
            'pass12345'
        )
        sample_recipe(user=user2, title='Chai Tea')
        sample_recipe(user=self.user, title='Barbecue')
        sample_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)
        
        all_recipes = Recipe.objects.all().order_by('-id')
        all_serializer = RecipeSerializer(all_recipes, many=True)
        authenticated_recipes = Recipe.objects.filter(user=self.user)
        authenticated_serializer = RecipeSerializer(authenticated_recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(len(all_serializer.data), 3)
        self.assertEqual(res.data, authenticated_serializer.data)
    
    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        # adding tags and ingredients in many-to-many relationships
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)



