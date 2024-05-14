from django.urls import path
from .views.index import index
from .views.Createuser import createuser
from .views.Createcompanies import createcompanies
from .views.role import role



urlpatterns = [
    
    path('', index.index_admin, name='admin'),
    path('users/', createuser.user_admin, name='user'),
    path('users/create', createuser.usercreate_admin, name='usercreate'),
    path('companies', createcompanies.createcompanies_admin, name='companies'),
    path('role', role.role_admin, name='role'),
    
]