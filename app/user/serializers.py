# we need the user model to create our serializer
from django.contrib.auth import get_user_model, authenticate
# translation system
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    # serializer for the user's object
    
    # specify the class meta inside
    class Meta:
        # call the model to base our serializer
        model = get_user_model()
        # specify fields we want to include in
        # convert to and from json
        fields = ('email','password','name')
        # configure extra settings in our model
        extra_kwargs = {'password':{'write_only':True, 'min_length':5}}
    # we can override the create function
    def create(self, validated_data):
        # create new user with encrypted password an return it
        # validated_data would be the json data passed as argument
        return get_user_model().objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    # Serializer for the user authentication object
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type':'password'},
        # allow whitespace inside passwords
        trim_whitespace=False
    )
    
    # attrs is every field that makes up our serializer as dictionary
    def validate(self, attrs):
        # validate and authenticate the user
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            # accesing the context request
            # passes the context into the serializer
            request = self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to authentiate with provided credentials')
            # how to handle the error
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs