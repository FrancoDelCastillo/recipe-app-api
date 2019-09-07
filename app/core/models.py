from django.db import models
# we need this to create or user manager class
# to extend our user model with import
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
# retrive our auth user model
from django.conf import settings

# Manage Class provides helper functions and overwrites to create user
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
        on_delete = models.CASCADE,
    )

    # string representation of the model
    def __str__(self):
        # we want to retrieve the name of the model
        return self.name
