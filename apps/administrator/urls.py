from django.urls import path
from .views.index import index
from .views.Createuser import createuser



urlpatterns = [
    
    path('', index.index_admin, name='admin'),
    path('users/', createuser.user_admin, name='user'),
    path('users/create', createuser.usercreate_admin, name='usercreate'),
    
]