from django.urls import path
from .views.index import index
from .views.payroll import payroll
from .views.pruebas import pruebas 
from .views.electronic_payroll import electronic_payroll


urlpatterns = [
    path('home/', index.index_payroll, name='index_payroll'),
    path('payroll/', payroll.payroll, name='payroll'),
    path('payroll/<str:id>', payroll.payrollview, name='payrollview'),
    path('payroll/pruebas/2', pruebas.vista_con_dos_formularios, name='vista_con_dos_formularios'),


    path('payroll/electronic_payroll/', electronic_payroll.electronic_payroll, name='nomina_electronica'),
]