from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento,Paises,Ciudades,Contratosemp,Profesiones,Contratos,Centrotrabajo

def EditContracsearch(request):
    empleados = Contratosemp.objects.using("lectaen").all()
    if request.method == 'POST':
        selected_option = request.POST['selected_option']
        return redirect('companies:editcontracvisual',selected_option)
    return render(request, './companies/EditContractSearch.html',{'empleados':empleados})


def EditContracVisual(request,idempleado):
    empleado = Contratosemp.objects.using("lectaen").get(idempleado=idempleado) 
    contrato =Contratos.objects.using("lectaen").get(idempleado=idempleado) 
    # CentroTrabajo = Centrotrabajo.objects.using("lectaen").get(idempleado=idempleado) 
    # centrotrabajo
    
    DicContract = {
        'Idcontrato':contrato.idcontrato , 
        'FechaTerminacion':contrato.fechafincontrato , 
        'Empleado':  empleado.papellido +' ' + empleado.sapellido +' ' + empleado.pnombre + ' ' + empleado.snombre + ' CC: ' + str(empleado.docidentidad) ,  #* esto es el nombre del empleado con su cedula  
        'TipoNomina':contrato.tiponomina , 
        'Cargo':contrato.cargo , 
        'LugarTrabajo': 'falta', #! validar de donde viene la informacion 
        'FechaInicial': contrato.fechafincontrato,
        'EstadoContrato': contrato.estadocontrato, 
        'TipoContrato':contrato.tipocontrato.tipocontrato, 
        'MotivoRetiro':contrato.motivoretiro, 
        'ModeloContrato':contrato.idmodelo.tipocontrato, 
        'Salario':"{:,.0f}".format(contrato.salario).replace(',', '.') , 
        'TipoSalario':contrato.tiposalario,
        'ModalidadSalario':contrato.tiposalario,
        # 'MotivoRetiro':contrato.motivoretiro,
        # 'MotivoRetiro':contrato.motivoretiro,
        # 'MotivoRetiro':contrato.motivoretiro,
        
    }
    
    
    return render(request, './companies/EditContractVisual.html',{'diccontract':DicContract})
