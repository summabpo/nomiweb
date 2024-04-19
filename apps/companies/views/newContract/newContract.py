from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento , Paises , Ciudades , Contratosemp,Profesiones

def newContractVisual(request):
    
    return render(request, './companies/newContractVisual.html')

def newContractCreater(request,idempleado):
    
    
    return render(request, './companies/newContractCreate.html')