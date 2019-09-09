from rest_framework import serializers

from core.models import Tag, Ingredient

# create model serializer link it to tag model and pull in the id and the name values
class TagSerializer(serializers.ModelSerializer):
    # Serializer for tag objects

    class Meta:
        model = Tag
        fields = ('id','name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    # serializer for ingredient objects

    class Meta:
        model = Ingredient
        fields = ('id','name')
        read_only_fields = ('id',)