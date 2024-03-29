from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

# the tag serializer to make the test pass
from recipe.serializers import TagSerializer


# for listing tags
TAGS_URL = reverse('recipe:tag-list')


# Test login required
class PublicTagsApiTest(TestCase):
    # Test the publicly available tags API

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # Test that login is required for retrieving tags
        # this makes and unauthenticated request to our tags API URL
        res = self.client.get(TAGS_URL)

        # verify this returns HTTP_401
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    # Test the authorized user tags API
    def setUp(self):
        # create a user
        self.user = get_user_model().objects.create_user(
            'test@email.com',
            'test1234'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        # Test retrieving tags
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        # make a http get request to TAGS URL
        res = self.client.get(TAGS_URL)
        # make the query on the model, reverse order by name
        tags = Tag.objects.all().order_by('-name')
        # serialize a list of objects many = True
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # data in the response is the same data in serializer
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        # test that tags returned are for the authenticated user
        # create a new user in addition to the user created at the setUp
        user2 = get_user_model().objects.create_user(
            'other@email',
            'test1234'
        )
        Tag.objects.create(user=user2, name='Fruity')
        # create a new tag assigned to authenticated user
        tag = Tag.objects.create(user=self.user, name='Comfort food')
        #
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # check the length of the result returned must be just one data
        self.assertEqual(len(res.data), 1)
        # test the name of the tag returned in the one response
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        # Test creating a new tag
        payload = {'name': 'test tag'}
        self.client.post(TAGS_URL, payload)
        # verify if the tag exists
        exists = Tag.objects.filter(
            # will filter all tags with the authenticated user
            # and with the name we create in our test
            user=self.user,
            name=payload['name']
            # returns True or False
            ).exists()
        self.assertTrue(exists)

    # test to see what happens if we create a tag with an invalid name
    def test_create_tag_invalid(self):
        # test creating a new tag invalid payload
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        # Test filtering tags by those assigned to recipes
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe1 = Recipe.objects.create(
            title='Coriander eggs on toast',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        # add a tag to this recipe
        recipe1.tags.add(tag1)

        # call our API
        # filter assigned_only tags
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        # verify lunch is not return because is not assigned to a recipe
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        # Test filtering tags by assigned returns unique items
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        # second tag to return
        Tag.objects.create(user=self.user, name='Lunch')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=10,
            price=3.00,
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=3,
            price=2.00,
            user=self.user
        )
        recipe2.tags.add(tag)

        # call our API
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        # verify if only 1 item is returned
        self.assertEqual(len(res.data), 1)
