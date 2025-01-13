from django.urls import path
from .views.index import index
from .views.payroll import payroll
from .views.pruebas import pruebas 
from .views.electronic_payroll import electronic_payroll


urlpatterns = [
    path('home/', index.index_payroll, name='index_payroll'),
    path('payroll/', payroll.payroll, name='payroll'),
    path('payroll/<str:id>', payroll.payrollview, name='payrollview'),
    path('payrollapi/', payroll.PayrollAPI.as_view(), name='payrollviewapi'),
    path('payroll/pruebas/2', pruebas.vista_con_dos_formularios, name='vista_con_dos_formularios'),
    path('payroll/electronic_payroll/', electronic_payroll.electronic_payroll_container, name='nomina_electronica'),
    path('payroll/generate_detail_electronic_payroll/<int:pk>', electronic_payroll.electronic_payroll_generate, name='generar_detalle_electronica'),

]