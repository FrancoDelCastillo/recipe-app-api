from unittest.mock import patch
# verify user created as expected
from django.test import TestCase
from django.contrib.auth import get_user_model
# import the models module from our core app
from core import models


# helper function to create users
def sample_user(email='test@email.com', password='test1234'):
    # create sample user
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user wit an email is successful"""
        email = 'test@email.com'
        password = 'test1234'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        # returns true if password is correct
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@EMAIL.COM'
        user = get_user_model().objects.create_user(email, 'test1234')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            # everything here should raises a value error
            get_user_model().objects.create_user(None, 'test1234')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@email.com', 'test1234')

        # assertion here
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    # creates a test model
    def test_tag_str(self):
        # test the tag string representation
        tag = models.Tag.objects.create(
            # calls the function and provides new user
            user=sample_user(),
            name='vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        # Test the ingredient string representation
        # verify if the model exists
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        # Tes the recipe string representacion
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='ceviche',
            time_minutes=10,
            price=20.00
        )

        self.assertEqual(str(recipe), recipe.title)

    #uuid module, uuid4 function to generate unique uid
    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        # test that image is saved in the correct location
        # mock the uid function from the default uid library
        # and change the value that returns
        uuid = 'test-uuid'
        # anytime we call uuid4 that is triggered from with in our test
        # it will change the value
        # overwrite the default behavior and return 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_patch(None, 'myimage.jpg')
        # expected path
        # literal string interpelation
        # insert variables inside string
        exp_path = f'uploads/recipe/{uuid}.jpg'

        self.assertEqual(file_path, exp_path)