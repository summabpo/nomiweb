from django.urls import path

from . import views

urlpatterns = [
    path('companies/init', views.startCompanies, name='startcompanies'),
    
    # ## server 
    # path('logout/', views.Logout, name='logout'),
]