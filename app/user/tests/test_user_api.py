from django.test import TestCase
# user model for our tests
from django.contrib.auth import get_user_model
# generate our api url
from django.urls import reverse

# rest framework to make request to our API and check response
from rest_framework.test import APIClient
from rest_framework import status

# Upcase for convention, constant variable for our URL

CREATE_USER_URL = reverse('user:create')
# add our URL to make the post request and generate our token
TOKEN_URL = reverse('user:token')

# **param is a dynamic list of arguments, we can add many arguments
def create_user(**params):
    # retrieve the user model 
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    # Test the users API (public)

    def setUp(self):
        # one client for all our tests
        self.client = APIClient()

    def test_create_valid_user_success(self):
        # test creating user with valid payload is successful
        payload = {
            'email' : 'test@email.com',
            'password' : 'testpass',
            'name' : 'Franco DC'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        # verify the response
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # take response data and pass it for get to create user
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

        def test_user_exists(self):
            # test creating a user that alredy exists fails
            payload = {'email':'test@email.com','password':'test1234'}
            create_user(**payload)
            res = self.client.post(CREATE_USER_URL, payload)

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        def test_password_too_short(self):
            # test that the password must be more than 5 characters
            payload = {'email':'test@email.com','password':'123'}
            res = self.client.post(CREATE_USER_URL, payload)
            
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            user_exists = get_user_model().objects.filter(email=payload['email']).exists()
            self.assertFalse(user_exists)
        
        def test_create_token_for_user(self):
            # Test that a token is created for the user
            payload = {'email':'test@email.com','password':'testpass'}
            # user that matches this authentication
            create_user(**payload)
            # token in the data response, HTTP 200
            res = self.client.post(TOKEN_URL, payload)
            # check if key token is in the response data
            self.assertIn('token', res.data)
            self.assertEqual(res.status_code,status.HTTP_200_OK)

        def test_create_token_invalid_credentials(self):
            # test that token is not created if invalid credentials are given
            create_user(email='test@email.com',password='testpass')
            payload = {'email':'test@email.com','password':'wrong'}
            # password incorrect we should get a post HTTP 400 bad request
            res = self.client.post(TOKEN_URL, payload)
            # verify token doenst exists in response data
            self.assertNotIn('token', res.data)
            assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
        def test_create_token_no_user(self):
            # test that token is not created if user doesn't exist
            payload = {'email':'test@email.com','password':'testpass'}
            res = self.client.post(TOKEN_URL,payload)

            self.assertNotIn('token',res.data)
            self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        
        def test_create_token_missing_field(self):
            # test that email and password are required
            res = self.client.post(TOKEN_URL,{'email':'one','password':''})

            self.assertNotIn('token',res.data)
            self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

