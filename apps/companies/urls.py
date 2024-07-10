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
from .views.nominatedcertificate import nominatedcertificate
from .views.payrollsummary import payrollsummary
from .views.loginweb import loginweb
from .views.payrollsheet import payrollsheet
from .views.assetsview import assetsview
from .views.birthday import birthday
from .views.workcertificate import workcertificate

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

    
    
    path('employees/birthday',birthday.BirthdayView.as_view() , name='birthdayview'),
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
    
    
    ##! nomina 
    path('payroll/labor/certification', laborcertification.laborcertification, name='laborcertification'),
    path('payroll/nominated/certificate', nominatedcertificate.nominatedcertificate, name='nominatedcertificate'),
    path('payroll/payroll/summary', payrollsummary.payrollsummary, name='payrollsummary'),
    path('payroll/payroll/sheet', payrollsheet.payrollsheet, name='payrollsheet'),
    
    path('payroll/payroll/summary/download/<int:idnomina>/', payrollsheet.generatepayrollsummary, name='generatepayrollsummary'),
    
    ##! seguridad 
    path('security/user', loginweb.loginweb, name='loginweb'),
    
    #// admin login 
    # path('logout/', views.Logout, name='logout'),
    path('', index.index_companies, name='index_companies'),
]

# EditResume
