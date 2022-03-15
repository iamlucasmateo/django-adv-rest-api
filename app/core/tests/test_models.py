from django.test import TestCase
# use get_user_model instead of importing User model directly
# in this way, if you modify what the user model is,
# the function get_user_model will still work correctly
# and your code will not break
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@test.com', password='123456'):
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):
    def test_create_user_with_email_successful(self):
        """Tests creating a user with email succeeds"""
        email = "test@testemail.com"
        password = "pass123"
        # customized user model (test fails with original)
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        # password cannot be changed directly, because it is hashed
        self.assertTrue(user.check_password(password))

    def test_create_new_user_email_normalized(self):
        """Tests new user has a normalized email"""
        email = 'test@DOMAIN.com'
        user = get_user_model().objects.create_user(email, '1234')
        self.assertEqual(user.email, 'test@domain.com')

    def test_new_user_invalid_email(self):
        """Test creating user with no error raises error"""
        # when testing that error should be raised
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '1234')

    def test_create_new_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'admin@admin.com',
            '1234'
        )
        self.assertEqual(user.email, 'admin@admin.com')
        self.assertTrue(user.check_password('1234'))

    def test_tag_str(self):
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual('Vegan', tag.name)

    def test_ingredients_str(self):
        """Test ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Garlic'
        )
        self.assertEqual(ingredient.name, str(ingredient))
    
    def test_recipe_str(self):
        """Test recipe str representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Mushroom cream',
            time_minutes=10,
            price=5.00
        )
        self.assertEqual(str(recipe), recipe.title)
