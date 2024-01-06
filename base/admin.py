from django.contrib import admin
from .models import senior_list,SMSMessage
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin 
from .models import osca_list

admin.site.register(osca_list)
# Register your models here.
admin.site.register(senior_list)
admin.site.register(SMSMessage)

#get rid of pre-registered Group
admin.site.unregister(Group)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name','last_name','username', 'email', 'is_staff', 'is_superuser', 'password1', 'password2'),
        }),
    )

# Unregister the default User admin
admin.site.unregister(User)

# Register the User model with the custom UserAdmin
admin.site.register(User, CustomUserAdmin)