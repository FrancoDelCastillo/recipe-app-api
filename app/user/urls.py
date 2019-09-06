# define paths in our app
from django.urls import path

from user import views

# define app name to identify
app_name = 'user'

urlpatterns = [
    # url to access the API
    path('create/',views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/',views.ManageUserView.as_view(), name='me')
]
