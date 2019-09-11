# rest framework generic modules
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    # Create a new user in the system
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    # Create a new auth token for user
    serializer_class = AuthTokenSerializer
    # set our renderer class to view the endpoint in the browser
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


# create manage user view
class ManageUserView(generics.RetrieveUpdateAPIView):
    # Manage the authenticated user
    serializer_class = UserSerializer
    # get the authenticated user and assigning it to request
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # add get object function to our API view
    # get the model for the logged in User
    def get_object(self):
        # Retrieve and return authentication user
        return self.request.user
