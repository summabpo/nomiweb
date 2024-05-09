from django.urls import path
from .views.ContractsList import ContractsList
from .views.newEmployee import newEmployee
from .views.EditEmployee import EditEmployee
from .views.editContract import editContract
from .views.newContract import newContract
from .views.charges import charges
from .views.Costcenter import Costcenter
from .views.index import index


urlpatterns = [
    ##todo novedades de nomina
    path('contract', ContractsList.startCompanies , name='startcompanies'),

    path('new/employee', newEmployee.newEmployee , name='newemployee'),
    path('edit/employee',  EditEmployee.EditEmployeeSearch , name='editemployeesearch'),
    
    path('edit/employee/<str:idempleado>',  EditEmployee.EditEmployeeVisual , name='editemployeevisual'),

    path('new/contract',newContract.newContractVisual ,name='newcontractvisual'),
    path('new/contract/<str:idempleado>',newContract.newContractCreater ,name='newcontractcreater'),

    path('edit/contract',editContract.EditContracsearch , name='editcontracsearch'),
    path('edit/contract/<str:idempleado>',editContract.EditContracVisual , name='editcontracvisual'),

    ##! empleados

    #! parametros 
    path('parameters/charges', charges.charges, name='charges'),
    path('parameters/Cost/center', Costcenter.Costcenter, name='costcenter'),
    
    
    ##! contabilidad 
    
    
    #* ## server -- errores 
    
    #// admin login 
    # path('logout/', views.Logout, name='logout'),
    path('', index.index_companies, name='index_companies'),
]

# EditResume
