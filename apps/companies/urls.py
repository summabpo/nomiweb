from django.urls import path

# # Importing views
from .views.ContractsList import ContractsList
from .views.newEmployee import newEmployee
from .views.EditEmployee import EditEmployee
from .views.editContract import editContract
from .views.newContract import newContract
from .views.charges import charges
from .views.Costcenter import Costcenter
from .views.workplace import workplace
from .views.headquarters import headquarters
from .views.hiring import hiring
# from .views.laborcertification import laborcertification
from .views.loginweb import loginweb
from .views.payrollsheet import payrollsheet
from .views.assetsview import assetsview
from .views.birthday import birthday
from .views.workcertificate import workcertificate
from .views.bank_list import bank_list
from .views.settlementlist import settlementlist
from .views.payrollaccumulations import payrollaccumulations
from .views.abstractconcept import abstractconcept

# # Accounting views
from .views.PayrollProvision import payrollprovision
from .views.externalreport import externalreport
from .views.dian import dian

# # Payroll News views
from .views.loans import loans
# from .views.disabilities import disabilities
from .views.vacation import vacation, vacation_general, vacation_balance, vacation_request

from .views.index import index

urlpatterns = [
    # ## Employee Contract URLs
    path('employees/contract/', ContractsList.startCompanies, name='startcompanies'),
    path('employees/excel0', ContractsList.exportar_excel0, name='exportar_excel0'),
    path('employees/excel1', ContractsList.exportar_excel1, name='exportar_excel1'),
    path('employees/excel2', ContractsList.exportar_excel2, name='exportar_excel2'),

    #hiring new items 
    path('employees/hiring/', hiring.hiring, name='hiring'),
    path('employees/hiring/contract', hiring.process_forms_contract, name='process_forms_contract'),
    path('employees/hiring/employee', hiring.process_forms_employee, name='process_forms_employee'),
    
    # ## Employee Management URLs
    # path('employees/new/employee', newEmployee.newEmployee, name='newemployee'),
    # path('employees/edit/employee', EditEmployee.EditEmployeeSearch, name='editemployeesearch'),
    path('employees/edit/employee/<str:idempleado>', EditEmployee.EditEmployeeVisual, name='editemployeevisual'),

    # ## Contract Management URLs
    # path('employees/new/contract', newContract.newContractVisual, name='newcontractvisual'),
    # path('employees/new/contract/<str:idempleado>', newContract.newContractCreater, name='newcontractcreater'),
    path('employees/edit/contract/<str:idempleado>', editContract.EditContracVisual, name='editcontracvisual'),

    # ## Work Certificate URLs
    path('employees/workcertificate/', workcertificate.workcertificate, name='workcertificate'),
    path('employees/workcertificate/generar_pdf/', workcertificate.generateworkcertificate, name='generateworkcertificate'),
    path('employees/workcertificate/generar_pdf/<int:idcert>', workcertificate.certificatedownload, name='certificatedownload'),

    # ## Birthday URL
    path('employees/birthday/', birthday.birthday_view, name='birthdayview'),

    # ## Asset Views URLs
    path('employees/views/contract/', assetsview.contractview, name='contractview'),
    path('employees/views/employee/', assetsview.resumeview, name='resumeview'),

    # ## Parameters URLs
    path('parameters/charges', charges.charges, name='charges'),
    path('parameters/charges/activate/<int:id>/', charges.toggle_charge_active_status, {'activate': True}, name='chargeactivate'),
    path('parameters/charges/deactivate/<int:id>/', charges.toggle_charge_active_status, {'activate': False}, name='chargedeactivate'),

    path('parameters/Cost/center', Costcenter.Costcenter, name='costcenter'),
    path('parameters/workplace', workplace.workplace, name='workplace'),
    path('parameters/headquarters', headquarters.headquarters, name='headquarters'),

    # ## Accounting URLs
    path('accounting/payroll/provision/', payrollprovision.payrollprovision, name='payrollprovision'),
    path('accounting/payroll/provision/download/', payrollprovision.payrollprovisiondownload_excel, name='payrollprovisiondownload_excel'),
    path('accounting/contributions/provision/', payrollprovision.contributionsprovision, name='contributionsprovision'),
    path('accounting/contributions/provision/download/', payrollprovision.contributionsprovisiondownload_excel, name='contributionsprovisiondownload_excel'),
    path('accounting/external/report/', externalreport.externalreport, name='externalreport'),
    path('accounting/external/report/download/', externalreport.download_excel_report, name='download_excel_report'),
    path('accounting/dian/certificate/', dian.viewdian, name='viewdian'),
    path('accounting/dian/certificate/download/<str:idingret>/', dian.viewdian_download, name='viewdian_download'),

    # ## Payroll URLs
    # path('payroll/labor/certification/', laborcertification.laborcertification, name='laborcertification'),
    path('payroll/sheet/', payrollsheet.payrollsheet, name='payrollsheet'),
    path('payroll/sheet/download/<int:idnomina>/<int:idcontrato>/', payrollsheet.generatepayrollcertificate, name='generatepayrollcertificate'),
    path('payroll/sheet/send/<int:idnomina>/<int:idcontrato>/', payrollsheet.unique_mail, name='unique_mail'),
    path('payroll/summary/download/<int:idnomina>/', payrollsheet.generatepayrollsummary, name='generatepayrollsummary'),
    path('payroll/summary/download/<int:idnomina>/all/', payrollsheet.generatepayrollsummary2, name='generatepayrollsummary2'),
    path('payroll/bank/list/get/', bank_list.bank_list_get, name='bank_list_get'),
    path('payroll/bank/list/file/<int:idnomina>/', bank_list.bank_file, name='bank_file'),
    path('payroll/settlement/list/', settlementlist.settlementlist, name='settlementlist'),
    path('payroll/settlement/download/<int:idliqui>/', settlementlist.settlementlistdownload, name='settlementlistdownload'),
    path('payroll/payroll/accumulations/', payrollaccumulations.payrollaccumulations, name='payrollaccumulations'),
    path('payroll/payroll/accumulations/download/', payrollaccumulations.descargar_excel_empleados, name='descargar_excel_empleados'),
    path('payroll/payroll/abstract/concept/', abstractconcept.abstractconcept, name='abstractconcept'),

    # ## Payroll News URLs
    path('payroll/new/loans/', loans.loans, name='loans'),
    # path('payroll/new/loans/edit/', loans.edit_loans, name='edit_loans'),
    # path('payroll/new/disabilities/', disabilities.disabilities, name='disabilities'),
    # path('payroll/new/disabilities/edit/', disabilities.edit_disabilities, name='edit_disabilities'),
    # path('payroll/new/disabilities/entity/', disabilities.get_entity, name='get_entity'),
    path('payroll/vacation/historical', vacation.vacation, name='vacation'),
    path('payroll/vacation/general/', vacation_general.vacation_general, name='vacation_general'),
    path('payroll/vacation/general/data/', vacation_general.get_novedades, name='get_novedades'),
    path('payroll/vacation/balance/', vacation_balance.vacation_balance, name='vacation_balance'),
    path('payroll/vacation/balance/download/', vacation_balance.vacation_balance_download, name='vacation_balance_download'),
    path('payroll/vacation/request/', vacation_request.vacation_request, name='vacation_request'),
    path('payroll/vacation/request/get/', vacation_request.get_vacation_details, name='get_vacation_details'),
    path('payroll/vacation/request/acction/', vacation_request.get_vacation_acction, name='get_vacation_acction'),

    # ## Mass Email URL
    path('payroll/sheet/massive/mail/', payrollsheet.massive_mail, name='massivemail'),

    # ## Security URLs
    path('security/user/', loginweb.loginweb, name='loginweb'),

    ## Admin Login URL (commented out)
    
    ## Index URL
    path('', index.index_companies, name='index_companies'),
]
