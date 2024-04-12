from django.urls import path

from . import views

urlpatterns = [
    path('', views.Login, name='login'),
    
    # ## server 
    # path('logout/', views.Logout, name='logout'),
]