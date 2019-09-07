from django.urls import path, include
# import a default router, automatically generates URL for our viewset
from rest_framework.routers import DefaultRouter

from recipe import views

# when you have a viewset you may have multiple URLs associated with that one viewset

router = DefaultRouter()
# register our view
router.register('tags',views.TagViewSet)
# define the app name
app_name = 'recipe'

urlpatterns = [
    # pass all the requests ''
    # generate all the urls
    path('', include(router.urls))
]