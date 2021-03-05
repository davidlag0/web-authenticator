'''webtools URL Configuration'''

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # TODO Could be added later with a change to NGINX config
    path('admin/', admin.site.urls),
    path('', include('webauth.urls')),
]
#] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
