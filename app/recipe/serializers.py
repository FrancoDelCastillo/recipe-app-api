from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


# create model serializer link it to tag model
# and pull in the id and the name values
class TagSerializer(serializers.ModelSerializer):
    # Serializer for tag objects

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    # serializer for ingredient objects

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    # serializer for recipe objects
    # listing only the ids
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'ingredients',
                  'tags', 'time_minutes', 'price', 'link')
        # prevent updating the foreign key
        read_only_fields = ('id',)


# Serialize a recipe detail using as base RecipeSerializer
class RecipeDetailSerializer(RecipeSerializer):
    # Nest serializers inside each other
    # read_only to work on our detail view
    # related key object return the ingredient
    # this object pass into ingredient serializer to convert it
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
