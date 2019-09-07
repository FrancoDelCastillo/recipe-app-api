#pull in different parts of a viewset to use for our application
# take the list model function, we dont want created, update, delete functions
from rest_framework import viewsets,mixins
# authenticate the request
from rest_framework.authentication import TokenAuthentication
# add the permission
from rest_framework.permissions import IsAuthenticated

# import the tag and the serializer
from core.models import Tag
from recipe import serializers


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
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