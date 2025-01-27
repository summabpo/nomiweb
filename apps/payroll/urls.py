from django.urls import path
from .views.index import index
from .views.payroll import payroll
from .views.plane import plane
from .views.electronic_payroll import electronic_payroll
from .views.parameters import parameters
from .views.pruebas import pruebas

urlpatterns = [
    path('home/', index.index_payroll, name='index_payroll'),
    path('payroll/', payroll.payroll, name='payroll'),
    path('payroll/<str:id>', payroll.payrollview, name='payrollview'),
    path('payrollapi/', payroll.PayrollAPI.as_view(), name='payrollviewapi'),
    path('payrollapi2/', payroll.PayrollAPI2.as_view(), name='payrollviewapi2'),
    path('payroll/electronic_payroll/', electronic_payroll.electronic_payroll_container, name='nomina_electronica'),
    path('payroll/detail_electronic_payroll/<int:pk>', electronic_payroll.electronic_payroll_detail, name='detalle_nomina_electronica'),
    path('payroll/generate_detail_electronic_payroll/<int:pk>', electronic_payroll.electronic_payroll_generate, name='generar_detalle_electronica'),
    path('payroll/generate_detail_electronic_payroll_ref/<int:pk>', electronic_payroll.electronic_payroll_generate_refactor, name='generar_detalle_electronica_ref'),
    
    ## plano 
    path('plane/<int:id>', plane.plane, name='plane'),
    path('document/', plane.document, name='document_plane'),
    
    #parametros
    path('parameters/bancks', parameters.banks, name='banks'),
    path('parameters/holidays', parameters.holidays, name='holidays'),
    path('parameters/entities', parameters.entities, name='entities'),
    path('parameters/fixed', parameters.fixed, name='fixed'),
    path('parameters/annual', parameters.annual, name='annual'),


    ## pruebas
    path('pruebas/<int:id>/<int:idnomina>/', pruebas.pruebas, name='pruebas'),

]