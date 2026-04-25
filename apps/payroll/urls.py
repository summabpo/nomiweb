from django.urls import path
from .views.index import index
from .views.payroll import payroll , payroll_automatic_systems , payroll_automatic_c
from .views.flat  import flat 
from .views.electronic_payroll import electronic_payroll
from .views.loans import loans
from .views.parameters import parameters
from .views.fixed import fixed
from .views.select_company import select_company
from .views.settlements import vacation_settlement , bonus_settlement , severance_settlement
from .views.family import family
from .views.time import time
from .views.accounting import benefits_provision 
from .views.accounting import security_provision
from .views.severance import severance
from .views.history import history 
from .views import liquidacion_pila
from .views.audit import ugpp_audit , payroll_excel
from .views.dian_certificates import income_withholding
from .views.withholding_tax import withholding
# afsa fsa asfad 

urlpatterns = [
    path('home/select/company', select_company.select_company, name='select_company'),
    path('home/', index.index_payroll, name='index_payroll'),
    path('payroll/', payroll.payroll, name='payroll'),
    path('payroll/<str:id>', payroll.payrollview, name='payrollview'),
    path('payroll/closet/<str:id>', payroll.payroll_closet, name='payroll_closet'),
    path('payroll/open/<str:id>', payroll.payroll_open, name='payroll_open'),
    path('payroll/audit/ugpp/<str:payroll_id>/<str:tipo_audit>/', ugpp_audit.UgppPayrollAudit, name='UgppPayrollAudit'),
    path('payroll/audit/excel/<str:payroll_id>/', payroll_excel.PayrollAuditExcel, name='PayrollAuditExcel'),
    path('payroll/audit/ugpp/employee/<str:payroll_id>/<str:idcontrato>/', ugpp_audit.audit_employee_payroll, name='audit_employee_payroll'),


    # dian certificates
    path('payroll/dian/certificates/income-withholding/', income_withholding.income_withholding_certificate, name='income_withholding_certificate'),
    path('payroll/dian/certificates/generate/income-withholding/', income_withholding.generate_income_withholding_certificate, name='generate_income_withholding_certificate'),
    path('payroll/dian/certificates/generate/income-withholding/excel/', income_withholding.generate_income_withholding_certificate_excel, name='generate_income_withholding_certificate_excel'),
    #electronic_payroll
    path('payroll/electronic_payroll/', electronic_payroll.electronic_payroll_container, name='nomina_electronica'),
    path('payroll/detail_electronic_payroll/<int:pk>', electronic_payroll.electronic_payroll_detail, name='detalle_nomina_electronica'),
    path('payroll/generate_detail_electronic_payroll/<int:pk>', electronic_payroll.electronic_payroll_generate_refactor, name='generar_detalle_electronica_ref'),
    path('payroll/electronic_payroll_regenerate/<int:pk>', electronic_payroll.electronic_payroll_regenerate, name='generar_detalle_individual'),
    path('payroll/electronic_payroll_validate_send/<int:pk>', electronic_payroll.electronic_payroll_validate_send, name='enviar_nomina_electronica'),
    path('payroll/electronic_payroll_validate_masive_send/<int:pk>', electronic_payroll.electronic_payroll_validate_masive_send, name='enviar_nomina_electronica_masiva'),
    path('payroll/electronic_payroll_detail_view/<int:pk>', electronic_payroll.electronic_payroll_detail_view, name='ver_nomina_electronica_detalle'),
    path('payroll/electronic_payroll_report_download/<int:pk>',electronic_payroll.electronic_payroll_report_download,name='electronic_payroll_report_download'),

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
    path('settlements/vacation/contract-info', vacation_settlement.vacation_contract_hire, name='vacation_contract_hire'),
    path('settlements/vacation/contract-history/<int:idcontrato>/', vacation_settlement.vacation_contract_history, name='vacation_contract_history'),
    path('settlements/vacation/calculate-periods', vacation_settlement.vacation_calculate_periods, name='vacation_calculate_periods'),
    path('settlements/vacation/delete', vacation_settlement.vacation_settlement_delete, name='vacation_settlement_delete'),
    path('settlements/vacation/', vacation_settlement.vacation_days_calc, name='vacation_days_calc'),
    
    path('settlements/bonus/p', bonus_settlement.bonus_p_settlement, name='bonus_p_settlement'),
    path('settlements/bonus/p/add/<str:fecha_init>/<str:fecha_fin>/<str:p>', bonus_settlement.bonus_p_settlement_add, name='bonus_p_settlement_add'),
    
    path('settlements/termination', severance_settlement.settlement_list, name='settlement_list'),
    path('settlements/termination/accrued/<str:id>/<str:fecha>', severance_settlement.settlement_accrued_values, name='settlement_accrued_values'),
    path('settlements/termination/payroll/<str:id>/<int:url>', severance_settlement.settlement_list_payroll, name='settlement_list_payroll'),
    
    
    path('severance/annual/', severance.severance_annual_calculation, name='severance_annual_calculation'),
    path('severance/monthly/<int:idc>/<int:year>', severance.severance_monthly_detail, name='severance_monthly_detail'),
    
    ### time 
    path('time/list', time.time_list, name='time_list'),
    path('time/list/doc/<str:id>', time.time_doc, name='time_doc'),
    
    # Accounting Module
    path('provisions/employee-benefits/', benefits_provision.employee_benefits_provision, name='employee_benefits_provision'),
    path('provisions/employee-benefits/download/', benefits_provision.export_employee_benefits_excel, name='export_employee_benefits_excel'),
    path('provisions/social-security/', security_provision.social_security_provision, name='social_security_provision'),
    path('provisions/social-security/download/', security_provision.export_social_security_excel, name='export_social_security_excel'),
    # PILA
    path('pila/liquidacion/', liquidacion_pila.liquidacion_pila, name='pila_liquidacion'),
    path('pila/planilla/<int:planilla_id>/txt/', liquidacion_pila.descargar_pila_txt, name='pila_descargar_txt'),
    path('pila/planilla/<int:planilla_id>/vista-txt/', liquidacion_pila.vista_plano_pila, name='pila_vista_txt'),
    path('pila/planilla/<int:planilla_id>/excel/', liquidacion_pila.descargar_pila_excel, name='pila_descargar_excel'),
    path('pila/planilla/<int:planilla_id>/json/', liquidacion_pila.descargar_pila_json, name='pila_descargar_json'),

    path('history/salary', history.history_salary, name='history_salary'),


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
    path('payroll/withholding/tax/<int:idnomina>/modal', withholding.withholding_tax, name='withholding_tax'),
    path('payroll/automatic_systems/<int:type_payroll>/<int:idnomina>/modal', payroll_automatic_systems.automatic_systems, name='automatic_systems'),
    path('payroll/automatic_systems_2/<int:type_payroll>/<int:idnomina>/<int:idcontrato>/modal', payroll_automatic_c.automatic_systems_2, name='automatic_systems_2'),
    
    ## flat
    path('flat/modal', flat.flat_modal, name='flat_modal'),
    
    # fixed concepts 
    path('fixed/modal', fixed.fixed_modal, name='fixed_modal'),
    path('fixed/modal/edit/<int:id>', fixed.fixed_modal_edit, name='fixed_modal_edit'),
    path('fixed/modal/edit/<int:id>/95', fixed.fixed_modal_edit_des, name='fixed_modal_edit_des'),
    path('fixed/modal/views/<int:id>/95', fixed.fixed_modal_views_historico, name='fixed_modal_views_historico'),


    path('parameters/concepts/add', parameters.concepts_add, name='concepts_add'),

    
    ## Time
    path('time/list/add', time.time_add, name='time_add'),
    path('time/list/data/<int:id>', time.time_data, name='time_data'),
    path('time/list/edit/<int:id>', time.time_edit, name='time_edit'),
    
    ## loans 
    path('payroll/loans/add', loans.employee_loans_modal_add, name='employee_loans_modal_add'),
    path('payroll/loans/data/<int:id>', loans.detail_employee_loans_modal, name='detail_employee_loans_modal'),
    path('payroll/loans/edit/<int:id>', loans.edit_employee_loans_modal, name='edit_employee_loans_modal'),
    
    
    ## vaca 
    path('payroll/vacation/add', vacation_settlement.vacation_settlement_add_list, name='vacation_settlement_add_list'),


    ## electronic payroll
    path('payroll/electronic_payroll_detail_view_template/<int:pk>', electronic_payroll.electronic_payroll_detail_view_template, name='electronic_payroll_detail_view_template'),
    
    path('history/salary/<int:id>', history.history_salary_details, name='history_salary_details'),
]

urlpatterns += urlunpolypatterns  
