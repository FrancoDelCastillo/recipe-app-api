# decorator to add a custom action to viewsets
from rest_framework.decorators import action
# returns a custom response
from rest_framework.response import Response
# generate status for our custom action
from rest_framework import viewsets, mixins, status
# authenticate the request
from rest_framework.authentication import TokenAuthentication
# add the permission
from rest_framework.permissions import IsAuthenticated

# import the tag and the serializer
from core.models import Tag, Ingredient, Recipe
from recipe import serializers


# new base class to refactor Tag and Ingredient viewsets
# listmodelmixin to give us support to list ingredients
class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    # Base viewset for user owned recipe attributes
    authentication_classes = (TokenAuthentication,)
    # requires tokenAuthentication is used
    # and user is authenticated to use the API
    permission_classes = (IsAuthenticated,)

    # function to override the get query set function
    def get_queryset(self):
        # Return objects for the current authenticated user only
        # the request objects should be passed in to the self
        # as a class variable
        # then the user should be assigned to that
        # because authentication is required
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


class RecipeViewSet(viewsets.ModelViewSet):
    # Manage recipes in the database
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # _ as common convention to indicate function itended to be private
    # qs as querystring
    def _params_to_ints(self, qs):
        # Returns a list of string IDs to a list of integers
        return [int(str_id) for str_id in qs.split(',')]

    # actions defined as functions in the viewset
    def get_queryset(self):
        # request object has a varible called query_params (is a dict)
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        # we dont want to reassign with the filter options
        queryset = self.queryset
        if tags:
            # converts a list of individual ids
            tag_ids = self._params_to_ints(tags)
            # tags__id__in django syntax for filtering on foreignkey objects
            # return all the tags where id is in this list we provide
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        # Retrieve the recipes for the authenticated user
        return queryset.filter(user=self.request.user)

    # override get_serializer_class function
    # this function is called to retrieve the serializer class
    # we have a number of actions available by default in ModelViewSet
    # 'retrieve' if we want to return DetailSerializer
    def get_serializer_class(self):
        # Return appropiate serializer class
        # verify the action being used for our current request
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        # check action
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        # Create a new recipe
        # assign the authenticated user to model once it has been created
        serializer.save(user=self.request.user)

    # define the method the action is going to accept
    # this action will be for the detail (specific recipe)
    # url_path is the path visible within the url
    # recipes/id/upload-image
    @action(methods=['POST'], detail=True, url_path='upload-image')
    # passed to the view as pk
    def upload_image(self, request, pk=None):
        # Upload an image to a recipe
        # retrieve the recipe object
        # get_object() gets the object that has been accessed
        # based on the id in the url
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        # validates the data and no extra field to been provided
        if serializer.is_valid():
            # saves on the recipe model with the updated data
            serializer.save()
            # contents serializer object uploaded (id's recipe and url's image)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        # add the default behavior (the invalid response)
        return Response(
            # return the errors for the serializers generated by drf
            # perform som
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
