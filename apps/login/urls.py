from django.urls import path
from . import views 



urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('prueba/', views.prueba, name='prueba'),
    path('permission/', views.require_permission, name='permission'),
    path('password/reset/',views.password_reset_view,name='reset' ),
    path('password/reset/<str:token>',views.password_reset_token,name='resettoken' ),
    
    
    
]