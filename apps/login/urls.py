from django.urls import path
from . import views 



urlpatterns = [
    path('', views.Login_view , name='login'),
    path('home/', views.login_home, name='login_home'),
    path('logout/', views.logout_view, name='logout'),
    path('error/', views.error_page, name='error_page'),
    path('permission/', views.require_permission, name='permission'),
    path('password/reset/',views.password_reset_view,name='reset' ),
    path('password/reset/<str:token>',views.password_reset_token,name='resettoken' ),
    
    
    
]