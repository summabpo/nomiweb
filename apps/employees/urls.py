from django.urls import path

from . import views

urlpatterns = [
    path('employees/index/', views.startemployees, name='login'),
    
    # ## server 
    # path('logout/', views.Logout, name='logout'),
]