from django.urls import path
from .views.index import index
from .views.Createuser import createuser 
from .views.Createcompanies import createcompanies
from .views.role import role
from .views.loginweb import loginweb 



urlpatterns = [
    
    path('', index.index_admin, name='admin'),
    path('users/', createuser.user_admin, name='user'),
    path('users/create/', createuser.usercreate_admin, name='usercreate'),
    path('users/activate/<int:user_id>/', createuser.toggle_user_active_status, {'activate': True}, name='useractivate'),
    path('users/deactivate/<int:user_id>/', createuser.toggle_user_active_status, {'activate': False}, name='userdeactivate'),

    path('companies/', createcompanies.createcompanies_admin, name='companies'),
    path('role/', role.role_admin, name='role'),
    path('loginweb/select/<str:empresa>/', loginweb.loginweb_admin, name='loginweb'),
    path('loginweb/select/',loginweb.select_loginweb_admin , name='logiwebselect'),
    path('loginweb/edit/<str:empresa>/',loginweb.edit_main , name='editmain'),
    
    
    
    
]