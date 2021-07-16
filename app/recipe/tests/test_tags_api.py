from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsAPITests(TestCase):
    """Test the public endpoints available under tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """should not allow to access the endpoint unauthenticated"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test the authenticated endpoints available under tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@mail.com",
            password="testpass"
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """should retrieve registered the tags"""
        Tag.objects.create(user=self.user, name="Chinese")
        Tag.objects.create(user=self.user, name="Arab")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """should retrieve the tags for an authenticated user"""
        user2 = get_user_model().objects.create_user(
            "other@mail.com",
            "pass123"
        )

        Tag.objects.create(user=user2, name="Fruit")
        tag = Tag.objects.create(user=self.user, name="Brazilian")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
