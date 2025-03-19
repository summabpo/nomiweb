from django.urls import path
from .views.index import index
from .views.payroll import payroll , payroll_automatic_systems
from .views.flat  import flat 
from .views.electronic_payroll import electronic_payroll
from .views.loans import loans
from .views.parameters import parameters
from .views.pruebas import pruebas

# afsa fsa

urlpatterns = [
    path('home/', index.index_payroll, name='index_payroll'),
    path('payroll/', payroll.payroll, name='payroll'),
    path('payroll/<str:id>', payroll.payrollview, name='payrollview'),


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
    path('parameters/concepts', parameters.concepts, name='concepts'),
    


    

]


urlhtmxpatterns =[
    
    
    path('parameters/concepts/add', parameters.concepts_add, name='concepts_add'),
    path('parameters/concepts/check/code', parameters.check_code, name='check_code'),
    
    
    

]

urlpatterns += urlhtmxpatterns  



urlunpolypatterns =[
    path('payroll/<int:id>/<int:idnomina>/modals/add', payroll.payroll_modal, name='payroll_modal'),
    path('payroll/modals/edit', payroll.payroll_edit, name='payroll_edit'),
    path('payroll/form/modals/create', payroll.payroll_create, name='payroll_create'),
    path('payroll/form/modals/delete', payroll.payroll_delete, name='payroll_delete'),
    path('payroll/form/calculate/<int:id>', payroll.payroll_calculate, name='payroll_calculate'),
    path('payroll/form/concept/', payroll.payroll_concept_info, name='payroll_concept_info'),
    path('payroll/form/concept/edit', payroll.payroll_info_edit, name='payroll_info_edit'),
    
    ## add employee
    path('payroll/<int:idnomina>/payroll_general', payroll.payroll_general, name='payroll_general'),
    path('payroll/<int:idnomina>/payroll_general/data', payroll.payroll_general_data, name='payroll_general_data'),
    
    # pruebas 
    path('items/', pruebas.index_item, name='index_item'),
    path('items/add/', pruebas.item_modal, name='item_modal'),
    path('items/add/modal', pruebas.add_item, name='add_item'),
    
    # segundas pruebas 
    path('my_form/', pruebas.my_form, name='my_form'),
    path('validate_number/', pruebas.get_multiplicador, name='get_multiplicador'),
    
    
    
    ## sitemas automaticos 
    
    path('payroll/automatic_systems/<int:type_payroll>/<int:idnomina>/modal', payroll_automatic_systems.automatic_systems, name='automatic_systems'),
    
    
]

urlpatterns += urlunpolypatterns  
