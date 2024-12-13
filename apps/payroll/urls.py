from django.urls import path
from .views.index import index
from .views.payroll import payroll



urlpatterns = [
    path('home/', index.index_payroll, name='index_payroll'),
    path('payroll/', payroll.payroll, name='payroll'),
]