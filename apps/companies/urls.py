from django.urls import path
from .views.ContractsList import ContractsList
from .views.newEmployee import newEmployee
from .views.EditEmployee import EditEmployee
from .views.editContract import editContract
from .views.newContract import newContract
from .views.charges import charges
from .views.Costcenter import Costcenter
from .views.workplace import workplace
from .views.headquarters import headquarters
from .views.laborcertification import laborcertification


from .views.loginweb import loginweb
from .views.payrollsheet import payrollsheet
from .views.assetsview import assetsview
from .views.birthday import birthday
from .views.workcertificate import workcertificate
from .views.bank_list import bank_list
from .views.settlementlist import settlementlist
from .views.payrollaccumulations import payrollaccumulations
from .views.abstractconcept import abstractconcept


# accounting
from .views.PayrollProvision import payrollprovision
from .views.externalreport import externalreport


# Payroll News
from .views.loans import loans
from .views.disabilities import disabilities
from .views.vacation import vacation

from .views.index import index


urlpatterns = [
    ##todo novedades de nomina
    path('employees/contract', ContractsList.startCompanies , name='startcompanies'),
    path('employees/excel1', ContractsList.exportar_excel1 , name='exportar_excel1'),
    path('employees/excel2', ContractsList.exportar_excel2 , name='exportar_excel2'),
    

    path('employees/new/employee', newEmployee.newEmployee , name='newemployee'),
    path('employees/edit/employee',  EditEmployee.EditEmployeeSearch , name='editemployeesearch'),
    
    path('employees/edit/employee/<str:idempleado>',  EditEmployee.EditEmployeeVisual , name='editemployeevisual'),

    path('employees/new/contract',newContract.newContractVisual ,name='newcontractvisual'),
    path('employees/new/contract/<str:idempleado>',newContract.newContractCreater ,name='newcontractcreater'),

    path('employees/edit/contract/<str:idempleado>',editContract.EditContracVisual , name='editcontracvisual'),
    
    
    path('employees/workcertificate/',workcertificate.workcertificate , name='workcertificate'),
    path('employees/workcertificate/generar_pdf/',workcertificate.generateworkcertificate , name='generateworkcertificate'),
    path('employees/workcertificate/generar_pdf/<int:idcert>',workcertificate.certificatedownload , name='certificatedownload'),

    
    
    path('employees/birthday',birthday.birthday_view , name='birthdayview'),
    ##! vistas 
    path('employees/views/contract/<str:idcontrato>',assetsview.contractview , name='contractview'),
    path('employees/views/employee/<str:idempleado>',assetsview.resumeview , name='resumeview'),
    

    ##! empleados
    

    #! parametros 
    path('parameters/charges', charges.charges, name='charges'),
    path('parameters/Cost/center', Costcenter.Costcenter, name='costcenter'),
    path('parameters/workplace', workplace.workplace, name='workplace'),
    path('parameters/headquarters', headquarters.headquarters, name='headquarters'),
    
    
    ##! contabilidad 
    path('accounting/payroll/provision', payrollprovision.payrollprovision, name='payrollprovision'),
    path('accounting/payroll/provision/download', payrollprovision.payrollprovisiondownload_excel, name='payrollprovisiondownload_excel'),
    path('accounting/contributions/provision', payrollprovision.contributionsprovision, name='contributionsprovision'),
    path('accounting/external/report', externalreport.externalreport, name='externalreport'),
    path('accounting/external/report/download', externalreport.download_excel_report, name='download_excel_report'),
    
    
    
    ##! Payroll
    path('payroll/labor/certification', laborcertification.laborcertification, name='laborcertification'),

    path('payroll/sheet', payrollsheet.payrollsheet, name='payrollsheet'),
    path('payroll/sheet/download/<int:idnomina>/<int:idcontrato>/', payrollsheet.generatepayrollcertificate, name='generatepayrollcertificate'),
    path('payroll/sheet/send/<int:idnomina>/<int:idcontrato>/', payrollsheet.unique_mail, name='unique_mail'),

    
    path('payroll/summary/download/<int:idnomina>/', payrollsheet.generatepayrollsummary, name='generatepayrollsummary'),
    path('payroll/summary/download/<int:idnomina>/all/', payrollsheet.generatepayrollsummary2, name='generatepayrollsummary2'),
    
    path('payroll/bank/list/get', bank_list.bank_list_get, name='bank_list_get'),
    path('payroll/bank/list/file/<int:idnomina>/', bank_list.bank_file, name='bank_file'),
    
    path('payroll/settlement/list', settlementlist.settlementlist, name='settlementlist'),
    path('payroll/settlement/download/<int:idliqui>/', settlementlist.settlementlistdownload, name='settlementlistdownload'),
    path('payroll/payroll/accumulations', payrollaccumulations.payrollaccumulations, name='payrollaccumulations'),
    path('payroll/payroll/accumulations/download', payrollaccumulations.descargar_excel_empleados, name='descargar_excel_empleados'),
    path('payroll/payroll/abstract/concept', abstractconcept.abstractconcept, name='abstractconcept'),
    
    
    ##! Payroll News
    path('payroll/new/loans', loans.loans, name='loans'),
    path('payroll/new/disabilities', disabilities.disabilities, name='disabilities'),
    path('payroll/new/vacation', vacation.vacation, name='vacation'),
    
    
        
    ##* masivos 
    path('payroll/sheet/massive/mail', payrollsheet.massive_mail, name='massivemail'),
    
    ##! seguridad 
    path('security/user', loginweb.loginweb, name='loginweb'),
    
    #// admin login 
    # path('logout/', views.Logout, name='logout'),
    path('', index.index_companies, name='index_companies'),
]

# EditResume
