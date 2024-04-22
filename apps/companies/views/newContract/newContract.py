from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento , Paises , Ciudades ,Contratosemp, Profesiones

from apps.companies.forms.EmployeeForm import ContractForm 

def newContractVisual(request):
    
    return render(request, './companies/newContractVisual.html')

def newContractCreater(request,idempleado):
    form = ContractForm()
    
    
    return render(request, './companies/newContractCreate.html',{'form':form})