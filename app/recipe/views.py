#pull in different parts of a viewset to use for our application
# take the list model function, we dont want created, update, delete functions
from rest_framework import viewsets,mixins
# authenticate the request
from rest_framework.authentication import TokenAuthentication
# add the permission
from rest_framework.permissions import IsAuthenticated

# import the tag and the serializer
from core.models import Tag, Ingredient
from recipe import serializers


class TagViewSet(viewsets.GenericViewSet, 
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    # Manage tags in the database
    authentication_classes = (TokenAuthentication,)
    # requires tokenAuthentication is used and user is authenticated to use the API
    permission_classes = (IsAuthenticated,)
    # add the queryset to return
    queryset = Tag.objects.all()
    # add the serializer
    serializer_class = serializers.TagSerializer

    # add a function to override the get query set function
    def get_queryset(self):
        # Return objects for the current authenticated user only
        # the request objects should be passed in to the self as a class variable
        # then the user should be assigned to that because authentication is required
        return self.queryset.filter(user=self.request.user).order_by('-name')
    
    # hook into the create process when creating an object 
    # when we do a create object in our viewset this function will be invoked
    # the validated serializer will be passed in as serializer argument
    # we can perform any modification to our create process
    def perform_create(self, serializer):
        # create a new tag
        # set the user to the authenticated user
        serializer.save(user=self.request.user)

# listmodelmixin to give us support to list ingredients
class IngredientViewSet(viewsets.GenericViewSet,mixins.ListModelMixin):
    # Manage ingredients in the database
    # add our authentication classes with token auth
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    
    def get_queryset(self):
        # Return objects for the current authenticated user
        return self.queryset.filter(user=self.request.user).order_by('-name')