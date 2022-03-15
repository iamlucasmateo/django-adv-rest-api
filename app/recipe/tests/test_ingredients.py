from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

# the syntax of reverse is 'app:endpoint-name'
INGREDIENTS_URL = reverse('recipe:ingredient-list')
CREATE_INGREDIENTS_URL = reverse('recipe:ingredient-create')


class PublicIngredientAPITest(TestCase):
    """Test the publicly available ingredients"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITest(TestCase):
    """Test ingredients can be retriever by authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='pass1234'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrievin list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that retriever ingredients are for user only"""
        user2 = get_user_model().objects.create(
            email='other@email.com',
            password='other_pass123'
        )
        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Wine')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
    
    def test_create_ingredient(self):
        res = self.client.post(CREATE_INGREDIENTS_URL, {'name': 'Lettuce'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        query_ingredient = Ingredient.objects.filter(name='Lettuce')[0]
        query_name = query_ingredient.name
        query_user_id = query_ingredient.user_id 
        self.assertEqual(query_name, 'Lettuce')
        self.assertEqual(query_user_id, self.user.id)

    def test_create_ingredient_invalid_input(self):
        res = self.client.post(CREATE_INGREDIENTS_URL, {'name': ''})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

