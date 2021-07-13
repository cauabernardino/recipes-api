from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Tests the public users endpoint"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """should create an user with valid parameters"""

        payload = {
            "email": "test@mail.com",
            "password": "test123",
            "name": "John Doe"
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))

        self.assertNotIn('password', res.data)

    def test_user_already_exists(self):
        """should not allow to create an user that already exists"""

        payload = {
            "email": "test2@mail.com",
            "password": "test123",
            "name": "John Doe"
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """should guarantee that the password is more than 5 chars"""

        payload = {
            "email": "test3@mail.com",
            "password": "ts",
            "name": "John Doe"
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """should create a token for the user with valid credentials"""

        payload = {
            "email": "test_token@mail.com",
            "password": "test123",
            "name": "John Doe"
        }
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """should fail to create a token with invalid user credentials"""

        # Right credentials
        payload1 = {
            "email": "test_token@mail.com",
            "password": "test123",
            "name": "John Doe"
        }
        # Wrong credentials
        payload2 = {
            "email": "test_token@mail.com",
            "password": "test789",
            "name": "John Doe"
        }
        create_user(**payload1)

        res = self.client.post(TOKEN_URL, payload2)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_inexistent_user(self):
        """should fail to create a token for inexistent user"""

        payload = {
            "email": "test_token@mail.com",
            "password": "test123",
            "name": "John Doe"
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """should fail to create a token for any missing required field"""

        payload = {
            "email": "test_token@mail.com",
            "password": "",
            "name": "John Doe"
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
