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



from .views.index import index


urlpatterns = [
    ##todo novedades de nomina
    path('employees/contract', ContractsList.startCompanies , name='startcompanies'),

    path('employees/new/employee', newEmployee.newEmployee , name='newemployee'),
    path('employees/edit/employee',  EditEmployee.EditEmployeeSearch , name='editemployeesearch'),
    
    path('employees/edit/employee/<str:idempleado>',  EditEmployee.EditEmployeeVisual , name='editemployeevisual'),

    path('employees/new/contract',newContract.newContractVisual ,name='newcontractvisual'),
    path('employees/new/contract/<str:idempleado>',newContract.newContractCreater ,name='newcontractcreater'),

    path('employees/edit/contract',editContract.EditContracsearch , name='editcontracsearch'),
    path('employees/edit/contract/<str:idempleado>',editContract.EditContracVisual , name='editcontracvisual'),
    
    
    

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
    
    
    ##! seguridad 
    path('security/user', loginweb.loginweb, name='loginweb'),
    
    #// admin login 
    # path('logout/', views.Logout, name='logout'),
    path('', index.index_companies, name='index_companies'),
]

# EditResume
