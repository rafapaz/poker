from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='main_index'),
    path('signup/', views.signup, name='main_signup'),
    path('signin/', views.signin, name='main_signin'),
    path('contact/', views.contact, name='main_contact'),
]