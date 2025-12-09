from django.urls import path
from .views.index import index
from .views.payroll import payroll , payroll_automatic_systems , payroll_automatic_c
from .views.flat  import flat 
from .views.electronic_payroll import electronic_payroll
from .views.loans import loans
from .views.parameters import parameters
from .views.pruebas import pruebas
from .views.fixed import fixed
from .views.select_company import select_company
from .views.settlements import vacation_settlement , bonus_settlement , severance_settlement
from .views.family import family
from .views.time import time
from .views.accounting import benefits_provision 
from .views.accounting import security_provision


# afsa fsa asfad 

urlpatterns = [
    path('home/select/company', select_company.select_company, name='select_company'),
    path('home/', index.index_payroll, name='index_payroll'),
    path('payroll/', payroll.payroll, name='payroll'),
    path('payroll/<str:id>', payroll.payrollview, name='payrollview'),
    path('payroll/closet/<str:id>', payroll.payroll_closet, name='payroll_closet'),


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
    #family
    path('parameters/family', family.family_list, name='family_list'),

    ## conceptos fijos 
    path('fixed', fixed.fixed, name='fixedconcepts'),


    ## settlements
    path('settlements/vacation', vacation_settlement.vacation_settlement, name='vacation_settlement'),
    path('settlements/vacation/add', vacation_settlement.vacation_settlement_add, name='vacation_settlement_add'),
    path('settlements/vacation/data/<str:id>/<str:t>', vacation_settlement.vacation_modal_data, name='vacation_modal_data'),
    path('settlements/vacation/', vacation_settlement.vacation_days_calc, name='vacation_days_calc'),
    
    path('settlements/bonus/p', bonus_settlement.bonus_p_settlement, name='bonus_p_settlement'),
    path('settlements/bonus/p/add/<str:fecha_init>/<str:fecha_fin>/<str:p>', bonus_settlement.bonus_p_settlement_add, name='bonus_p_settlement_add'),
    
    path('settlements/termination', severance_settlement.settlement_list, name='settlement_list'),
    path('settlements/termination/payroll/<str:id>/<int:url>', severance_settlement.settlement_list_payroll, name='settlement_list_payroll'),
    
    ### time 
    path('time/list', time.time_list, name='time_list'),
    path('time/list/doc/<str:id>', time.time_doc, name='time_doc'),
    
    # Accounting Module
    path('provisions/employee-benefits/', benefits_provision.employee_benefits_provision, name='employee_benefits_provision'),
    path('provisions/social-security/', security_provision.social_security_provision, name='social_security_provision'),
]


urlhtmxpatterns =[
    
    
    #path('parameters/concepts/add', parameters.concepts_add, name='concepts_add'),
    path('parameters/concepts/check/code', parameters.check_code, name='check_code'),
    
    
    

]

urlpatterns += urlhtmxpatterns  



urlunpolypatterns =[
    
    path('payroll/modal/create/', payroll.payroll_create_add, name='payroll_create_add'),
    
    path('payroll/<int:id>/<int:idnomina>/modals/add', payroll.payroll_modal, name='payroll_modal'),
    path('payroll/modals/edit', payroll.payroll_edit, name='payroll_edit'),
    path('payroll/form/modals/create', payroll.payroll_create, name='payroll_create'),
    path('payroll/form/modals/create-nomina', payroll.payroll_create_nomina_modal, name='create_nomina_modal'),
    path('payroll/form/modals/delete', payroll.payroll_delete, name='payroll_delete'),
    path('payroll/form/calculate/<int:id>', payroll.payroll_calculate, name='payroll_calculate'),
    path('payroll/form/concept/', payroll.payroll_concept_info, name='payroll_concept_info'),
    path('payroll/form/concept/edit', payroll.payroll_info_edit, name='payroll_info_edit'),
    
    ## add employee
    path('payroll/<int:idnomina>/payroll_general', payroll.payroll_general, name='payroll_general'),
    path('payroll/<int:idnomina>/payroll_general/data', payroll.payroll_general_data, name='payroll_general_data'),
        
    
    path('parameters/concepts/detail/modal/<int:id>', parameters.concepts_detail, name='concepts_detail'),
    path('parameters/concepts/edit/modal/<int:id>', parameters.concepts_edit, name='concepts_edit'),
    
    path('parameters/family/add/modal/', family.family_create, name='family_create'),
    path('parameters/family/detail/modal/<int:id>', family.family_detail, name='family_detail'),
    path('parameters/family/edit/modal/<int:id>', family.family_edit, name='family_edit'),
    path('parameters/family/delete/modal/<int:id>', family.family_delete, name='family_delete'),
    
    path('parameters/fixed/add', parameters.fixed_add, name='fixed_add'),
    path('parameters/fixed/edit/<str:id>', parameters.fixed_edit, name='fixed_edit'),
    
    path('settlements/termination/add/modal/', severance_settlement.settlement_create, name='settlement_create'),
    path('settlement/termination/calculate/', severance_settlement.settlement_calculate, name='settlement_calculate'),
    
    #path('parameters/family', family.family_list, name='family_list'),
    ## sitemas automaticos 
    
    path('payroll/automatic_systems/<int:type_payroll>/<int:idnomina>/modal', payroll_automatic_systems.automatic_systems, name='automatic_systems'),
    path('payroll/automatic_systems_2/<int:type_payroll>/<int:idnomina>/<int:idcontrato>/modal', payroll_automatic_c.automatic_systems_2, name='automatic_systems_2'),
    
    ## flat
    path('flat/modal', flat.flat_modal, name='flat_modal'),
    
    # fixed concepts 
    path('fixed/modal', fixed.fixed_modal, name='fixed_modal'),
    path('parameters/concepts/add', parameters.concepts_add, name='concepts_add'),

    ### pruebas 
    path('payroll/modal/pruebas', pruebas.prueba, name='prueba'),
    path('payroll/modal/pruebas/modal', pruebas.prueba_modal, name='prueba_modal'),
    
    
    ## Time
    path('time/list/add', time.time_add, name='time_add'),
    path('time/list/data/<int:id>', time.time_data, name='time_data'),
    path('time/list/edit/<int:id>', time.time_edit, name='time_edit'),
    
    ## loans 
    path('payroll/loans/add', loans.employee_loans_modal_add, name='employee_loans_modal_add'),
    path('payroll/loans/data/<int:id>', loans.detail_employee_loans_modal, name='detail_employee_loans_modal'),
]

urlpatterns += urlunpolypatterns  
