from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer


# create our URL
INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsAPiTest(TestCase):
    # Test the publicly available ingredients API

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # test that login is required to access the endpoint
        # make the get request to the url
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# testing listing our ingredients
class PrivateIngredientsApiTest(TestCase):
    # Test the private ingredients API

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@email.com',
            'test1234'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        # Test retrieving a list of ingredients
        Ingredient.objects.create(user=self.user, name='Avocado')
        Ingredient.objects.create(user=self.user, name='salt')
        # make our request
        res = self.client.get(INGREDIENTS_URL)
        # verify the return result matches with the expected
        # we retrieve all the ingredients, serialize them and then
        # compare the result to the serialized ingredients
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_ingredients_limited_to_user(self):
        # Test that ingredients for the authenticated user are returned
        # new user
        user2 = get_user_model().objects.create_user(
            'other@email.com',
            'test1234'
        )
        # ingredient object for new user
        Ingredient.objects.create(user=user2, name='Vinegar')
        # another ingredient assigned to authenticated user
        # we will check that the name of this ingredient matches
        # with the name if the ingredient we created
        ingredient = Ingredient.objects.create(user=self.user, name='Tumeric')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        # test create a new ingredient
        payload = {'name': 'cabbage'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        # Test creating invalid ingredient fails
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        # Test filtering ingredients by those assigned to recipes
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Apples'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Turkey'
        )
        recipe1 = Recipe.objects.create(
            title='Apple crumble',
            time_minutes=5,
            price=10.00,
            user=self.user
        )

        recipe1.ingredients.add(ingredient1)

        # call our API
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredient_assigned_unique(self):
        # Test filtering ingredients by assigned returns unique items
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Eggs'
        )
        # secondary ingredient
        Ingredient.objects.create(
            user=self.user,
            name='Milk'
        )
        recipe1 = Recipe.objects.create(
            title='Egg benedict',
            time_minutes=15,
            price=12.00,
            user=self.user
        )
        recipe1.ingredients.add(ingredient1)
        recipe2 = Recipe.objects.create(
            title='Coriander eggs on toast',
            time_minutes=20,
            price=5.00,
            user=self.user
        )
        recipe2.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
