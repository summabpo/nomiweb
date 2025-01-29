from django.urls import path
from .views.index import index
from .views.payroll import payroll
from .views.flat  import flat 
from .views.electronic_payroll import electronic_payroll
from .views.loans import loans
from .views.parameters import parameters
from .views.pruebas import pruebas

urlpatterns = [
    path('home/', index.index_payroll, name='index_payroll'),
    path('payroll/', payroll.payroll, name='payroll'),
    path('payroll/<str:id>', payroll.payrollview, name='payrollview'),
    path('payrollapi/', payroll.PayrollAPI.as_view(), name='payrollviewapi'),
    path('payrollapi2/', payroll.PayrollAPI2.as_view(), name='payrollviewapi2'),
    #path('payroll/pruebas/2', pruebas.vista_con_dos_formularios, name='vista_con_dos_formularios'),

    #electronic_payroll
    path('payroll/electronic_payroll/', electronic_payroll.electronic_payroll_container, name='nomina_electronica'),
    path('payroll/detail_electronic_payroll/<int:pk>', electronic_payroll.electronic_payroll_detail, name='detalle_nomina_electronica'),
    path('payroll/generate_detail_electronic_payroll/<int:pk>', electronic_payroll.electronic_payroll_generate_refactor, name='generar_detalle_electronica_ref'),
    path('payroll/electronic_payroll_regenerate/<int:pk>', electronic_payroll.electronic_payroll_regenerate, name='generar_detalle_individual'),
    path('payroll/electronic_payroll_validate_send/<int:pk>', electronic_payroll.electronic_payroll_validate_send, name='enviar_nomina_electronica'),
    path('payroll/electronic_payroll_validate_masive_send/<int:pk>', electronic_payroll.electronic_payroll_validate_masive_send, name='enviar_nomina_electronica_masiva'),
    path('payroll/electronic_payroll_detail_view/<int:pk>', electronic_payroll.electronic_payroll_detail_view, name='ver_nomina_electronica_detalle'),
    
    #loans
    path('loans', loans.employee_loans, name='loans_list'),
    path('loans_detail/<int:pk>', loans.detail_employee_loans, name='loans_detail'),
    path('api_detail_payroll_loan/<int:pk>', loans.api_detail_payroll_loan, name='api_loans_detail'),

    ## plano 
    path('flat/<int:id>', flat.flat , name='flat'),
    path('document/', flat.document, name='document_flat'),
    
    #parametros
    path('parameters/bancks', parameters.banks, name='banks'),
    path('parameters/holidays', parameters.holidays, name='holidays'),
    path('parameters/entities', parameters.entities, name='entities'),
    path('parameters/fixed', parameters.fixed, name='fixed'),
    path('parameters/annual', parameters.annual, name='annual'),


    ## pruebas
    path('pruebas/<int:id>/<int:idnomina>/', pruebas.pruebas, name='pruebas'),

]