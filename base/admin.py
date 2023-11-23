from django.contrib import admin
from .models import senior_list,SMSMessage
from django.contrib.auth.models import Group

# Register your models here.
admin.site.register(senior_list)
admin.site.register(SMSMessage)
#get rid of pre-registered Group
admin.site.unregister(Group)