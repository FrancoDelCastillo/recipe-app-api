from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# converting tring in python to human readable text
from django.utils.translation import gettext as _

from core import models


# extends the base user admin
class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    # define the sections in our change and create page
    # first part is the tittle of the section
    # second part contains the fields
    fieldsets = (
        (None, {'fields':('email','password')}
            ),
        (_('Personal Info'),{'fields':('name',)}
            ),
        (_('Permissions'),
            {'fields':('is_active','is_staff','is_superuser')}
        ),
        (_('Important dates'), {'fields':('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes':('wide',),
            'fields': ('email','password1','password2')
        }),
    )

admin.site.register(models.User, UserAdmin)
# we dont need to specify the admin tht we want to register with
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)