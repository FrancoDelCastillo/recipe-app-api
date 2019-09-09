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


# new base class to refactor Tag and Ingredient viewsets
# listmodelmixin to give us support to list ingredients
class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    # Base viewset for user owned recipe attributes
    authentication_classes = (TokenAuthentication,)
    # requires tokenAuthentication is used and user is authenticated to use the API
    permission_classes = (IsAuthenticated,)
    
    # function to override the get query set function
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
        # Create a new object (tag, ingredient)
        # set the user to the authenticated user
        serializer.save(user=self.request.user)
    

# Manage tags in the database
class TagViewSet(BaseRecipeAttrViewSet):
    # Model referenced in the query
    queryset = Tag.objects.all()
    # serializer that is used
    serializer_class = serializers.TagSerializer

# Manage ingredients in the database
class IngredientViewSet(BaseRecipeAttrViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer