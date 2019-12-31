from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='main_index'),
    path('signup/', views.signup, name='main_signup'),
    path('signin/', views.signin, name='main_signin'),
    path('signout/', views.signout, name='main_signout'),
    path('contact/', views.contact, name='main_contact'),
    path('ack/', views.ack, name='main_ack'),
    path('update_money/', views.update_money, name='main_update_money'),
    path('play/', views.play, name='main_play'),
]