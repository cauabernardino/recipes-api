from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email="test@mail.com", password="testpass"):
    """Creates a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """should create an user with its email"""

        email = "test@testmail.com"
        password = "TestPass123"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_new_user_email(self):
        """should lowercase the email for a new user"""

        email = "test@TESTMAIL.com"
        password = "TestPass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """should fail if user inserts invalid email"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_super_user(self):
        """should create a superuser"""
        email = "test@testmail.com"
        password = "TestPass123"

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="Italian"
        )

        self.assertEqual(str(tag), tag.name)
