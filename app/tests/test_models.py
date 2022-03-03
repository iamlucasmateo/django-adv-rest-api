from django.test import TestCase
# use get_user_model instead of importing User model directly
# in this way, if you modify what the user model is, 
# the function get_user_model will still work correctly
# and your code will not break 
from django.contrib.auth import get_user_model

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
        # password cannot be changed directly
        self.assertTrue(user.check_password(password))
