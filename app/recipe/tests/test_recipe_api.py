import tempfile
# allows to create path name and check if file exists in system
import os

# image model from pillow libry
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
    # Return URL for recipe image upload
    # recipe:name-of-the-custom-url for an endpoint
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_url(recipe_id):
    # Return recipe detail URL
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    # Create and return a sample tag
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    # Create and return a sample ingredient
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    # Create and return a sample recipe
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPiTests(TestCase):
    # Test unauthenticated recipe API access

    def setUp(self):
        self.client = APIClient()

    def test_auth_requiered(self):
        # Test that authentication is required
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    # Test unauthenticated recipe API access

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@email.com',
            'test1234'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        # Test retrieving a list of recipes
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        # we want to return the data as list, many = True
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        # Test retrieving recipes for user
        user2 = get_user_model().objects.create_user(
            'test2@email',
            'test1234'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        # filter our recipes
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        # Test viewing a recipe detail
        recipe = sample_recipe(user=self.user)
        # add an item to many-to-many field on recipe model
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        # we want to serialize a single object
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        # Test creating recipe
        payload = {
            'title': 'Chocolate cake',
            'time_minutes': 30,
            'price': 10.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # retrieve created recipe from our model
        recipe = Recipe.objects.get(id=res.data['id'])
        # standard function to loop into each key in dict payload
        for key in payload.keys():
            # standard function getattr() to retrieve attributes from an object
            # by passing in a variable instead of dot notation (.tilte,.price)
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        # Test creating a recipe with tags
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'Avodaco lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        # post the payload
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        # return all the tags assigned to our recipe
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        # Test creating recipe with ingredients
        ingredient1 = sample_ingredient(user=self.user, name='Praws')
        ingredient2 = sample_ingredient(user=self.user, name='Ginger')
        # create a sample recipe
        payload = {
            'title': 'Thai prawn red curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
            'price': 8.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        # get the ingredients queryset
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        # Test updating a recipe with patch (update fields provided)
        # make a request to change our field in recipe
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')
        payload = {
            'title': 'Chicken tikka',
            'tags': [new_tag.id]
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        # refreshes our details in our recipe from the database
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        # retrieve all the tags assigned to the recipe
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        # check if new_tag is in tags we retrieved
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        # Test updating a recipe with put
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Spaghetti carbonara',
            'time_minutes': 25,
            'price': 5.00
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        # check tags assigned are zero because it has a sample_tag assigned
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):
    # this runs before the test
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@email.com',
            'test1234'
        )
        # authenticate the user
        self.client.force_authenticate(self.user)
        # we want a recipe already created for test
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        # removing tests files we create
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        # Test uploading an image to recipe
        url = image_upload_url(self.recipe.id)
        # context manager creates a named temporary file on system
        # open as ntf but it removes outside the with statement
        # suffix extention we want to use
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            # create an image with pillow library
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            # with save we read up to the end of the file
            # sets the pointer back to the beginning of the file
            ntf.seek(0)
            # second argument is the payload of just image
            # add format to our post, by default for consists of a Json object
            res = self.client.post(url, {'image': ntf}, format='multipart')

            self.recipe.refresh_from_db()
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            # check if image is in response so path should be accesible
            self.assertIn('image', res.data)
            # check that the path exists for the image saved in model
            self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        # Test uploading an invalid image
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'not image'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
