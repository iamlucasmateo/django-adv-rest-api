from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


# shorten create user
def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTests(TestCase):
    """Tests the Users API, public endpoints"""
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_access(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'han_solo@test.com',
            'password': 'chewbacca',
            'name': 'Han Solo'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # the response includes the created user, lets's test that
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating user that already exists"""
        user_data = {
            'email': 'han_solo@test.com',
            'password': 'chewbacca',
            'name': 'Han Solo'
        }
        create_user(**user_data)
        res = self.client.post(CREATE_USER_URL, user_data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test password is more than 5 characters"""
        payload = {
            'email': 'luke@sky.com',
            'password': 'han',
            'name': 'Luke'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test a token is created for the user"""
        payload = {
            'email': 'email@test.com',
            'password': '123456'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are used"""
        user_data = {
            'email': 'email@test.com',
            'password': '123456',
            'name': 'Homer Simpson'
        }
        create_user(**user_data)
        payload = user_data.update({'password': 'wrong_pass'})
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {
            'email': '34qyaevwargafv@sdfbasetrhsrtg.com',
            'password': '1234657432',
            'name': 'John'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_password(self):
        """Test that email and password are created"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_email(self):
        res = self.client.post(TOKEN_URL, {'password': '123456'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required on endpoint"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    # setup will generate an authenticated user
    def setUp(self):
        self.user = create_user(
            email='someone@testing.com',
            password='123456',
            name='Test user'
        )
        self.client = APIClient()
        # this method simulates authenticated requests
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the url"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test update works"""
        payload = {
            'name': 'New Name',
            'password': 'new_pass'
        }
        res = self.client.patch(ME_URL, payload)
        # this method refreshes the data from the user
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
