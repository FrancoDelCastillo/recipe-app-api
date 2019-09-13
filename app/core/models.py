import uuid
import os
from django.db import models
# we need this to create or user manager class
# to extend our user model with import
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
# retrive our auth user model
from django.conf import settings


def recipe_image_file_patch(instance, filename):
    # Generate file path for new recipe image
    # split in list separated by .
    # [-1] slice the list and return the last item (jpg)
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/recipe/', filename)


# Manage Class provides helper functions and overrides to create user
class UserManager(BaseUserManager):
    # Creates and saves a new user
    # **extra_fields adds additional fields to our model
    def create_user(self, email, password=None, **extra_fields):
        # raise ValueError if email wasn't provided when function was called
        if not email:
            raise ValueError('Users must have an email address')
        # normalize_email is a helper function from BaseUserManager
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # Password encrypted with set_password
        user.set_password(password)
        # supporting multiple databases with _db
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


""" Custom user model extending AbstractBaseUser and PermissionsMixin
supports using email instead of username """


class User(AbstractBaseUser, PermissionsMixin):

    # define the fields for our database model
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # assign user manager to the objects attribute
    objects = UserManager()

    # customize to use email instead of username
    USERNAME_FIELD = 'email'


class Tag(models.Model):
    # Tag to be use for a recipe
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        # the first argument is the model we want to base the foreing key off
        settings.AUTH_USER_MODEL,
        # specify what we want to happens to the tags when we delete a user
        on_delete=models.CASCADE
    )

    # string representation of the model
    def __str__(self):
        # we want to retrieve the name of the model
        return self.name


class Ingredient(models.Model):
    # Ingredient to be used in a recipe
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    # Recipe object
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    # optional field with blank
    # with null we have to check if the field is blank or has a value
    link = models.CharField(max_length=255, blank=True)
    # many to many fields as Foreign key and the name of the class as parameter
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(null=True, upload_to=recipe_image_file_patch)

    def __str__(self):
        return self.title
