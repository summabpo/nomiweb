from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento , Paises , Ciudades , Contratosemp,Profesiones

def newContractVisual(request):
    empleados = Contratosemp.objects.using("lectaen").filter(estadocontrato=4)
    return render(request, './companies/newContractVisual.html',{'empleados':empleados})

def newContractCreater(request,idempleado):
    
    
    return render(request, './companies/newContractCreate.html')