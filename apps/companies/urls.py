from django.urls import path
from .views.ContractsList import ContractsList
from .views.Resume import editresume


urlpatterns = [
    ##todo novedades de nomina 
    path('companies/init', ContractsList.startCompanies , name='startcompanies'),
    path('companies/new/employee', editresume.newEmployee , name='newemployee'),
    
    
    
    ##! empleados 
    
    ##! parametros 
    
    ##! contabilidad 
    
    
    #* ## server -- errores 
    
    ##// admin login 
    # path('logout/', views.Logout, name='logout'),
]

# EditResume
