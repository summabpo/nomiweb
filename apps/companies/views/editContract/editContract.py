from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento,Paises,Ciudades,Contratosemp,Profesiones,Contratos

def EditContracsearch(request):
    empleados = Contratosemp.objects.using("lectaen").all()
    if request.method == 'POST':
        selected_option = request.POST['selected_option']
        #return redirect('main:costos', proyecto.codigo )
        return redirect('companies:editcontracvisual',selected_option)
    return render(request, './companies/EditContractSearch.html',{'empleados':empleados})


def EditContracVisual(request,idempleado):
    empleado = Contratosemp.objects.using("lectaen").get(idempleado=idempleado) 
    contrato =Contratos.objects.using("lectaen").get(idempleado=idempleado) 
    return render(request, './companies/EditContractVisual.html')
