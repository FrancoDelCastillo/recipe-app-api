# verify user created as expected
from django.test import TestCase
from django.contrib.auth import get_user_model
# import the models module from our core app
from core import models

# helper function to create users
def sample_user(email='test@email.com',password='test1234'):
    # create sample user
    return get_user_model().objects.create_user(email,password)

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

        self.assertEqual(str(tag),tag.name)