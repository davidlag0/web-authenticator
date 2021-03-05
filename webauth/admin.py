'''Admin configuration for webauth'''
from django.contrib import admin
from .models import User, Tool, UserAccess

admin.site.register(User)
admin.site.register(Tool)
admin.site.register(UserAccess)
