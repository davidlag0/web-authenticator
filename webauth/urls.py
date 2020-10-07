'''webauth URLs'''
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('login/<str:tool>/', views.login, name='login'),
    path('logout', views.logout, name='logout')
]
