'''webtools URL Configuration'''

# from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('webauth.urls')),

    # TODO Could be added later with a change to NGINX config
    # path('admin/', admin.site.urls),
]
