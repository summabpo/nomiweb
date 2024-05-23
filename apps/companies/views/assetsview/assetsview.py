from django.shortcuts import render
from apps.companies.models import Contratos , Contratosemp


def contractview(request,idcontrato): 
    contrato = Contratos.objects.get(idcontrato = idcontrato)
    
    return render(request, './companies/contractview.html',{'contrato': contrato })


def resumeview(request,idempleado): 
    empleados = Contratosemp.objects.get(idempleado = idempleado)
    
    return render(request, './companies/resumeview.html',{'empleados': empleados })