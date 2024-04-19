from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento , Paises , Ciudades , Contratosemp,Profesiones

def newContract(request):
    
    return render(request, './companies/NewEmployee.html')