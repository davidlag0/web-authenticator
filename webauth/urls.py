'''webauth URLs'''
from django.urls import path

from . import views

urlpatterns = [
    path('<str:tool>', views.index, name='index'),
    path('login/<str:tool>', views.login, name='login'),
    path('logout', views.logout, name='logout')
]
