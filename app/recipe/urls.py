from django.urls import path, include
# import a default router, automatically generates URL for our viewset
from rest_framework.routers import DefaultRouter

from recipe import views

# viewset may have multiple URLs associated with one viewset

router = DefaultRouter()
# register our views
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)

# define the app name
app_name = 'recipe'

urlpatterns = [
    # pass all the requests ''
    # generate all the urls
    path('', include(router.urls))
]
