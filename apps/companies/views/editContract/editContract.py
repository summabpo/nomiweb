from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento,Paises,Ciudades,Contratosemp,Profesiones,Contratos,Centrotrabajo

def EditContracsearch(request):
    empleados = Contratosemp.objects.using("lectaen").filter(estadocontrato=1)
    if request.method == 'POST':
        selected_option = request.POST['selected_option']
        return redirect('companies:editcontracvisual',selected_option)
    return render(request, './companies/EditContractSearch.html',{'empleados':empleados})


def EditContracVisual(request,idempleado):
    empleado = Contratosemp.objects.using("lectaen").get(idempleado=idempleado) 
    contrato =Contratos.objects.using("lectaen").get(idempleado=idempleado,estadocontrato=1) 
    # CentroTrabajo = Centrotrabajo.objects.using("lectaen").get(idempleado=idempleado) 
    # centrotrabajo
    
    DicContract = {
        #Contrato
        'Idcontrato':contrato.idcontrato , 
        'FechaTerminacion':contrato.fechafincontrato , 
        'Empleado':  empleado.papellido +' ' + empleado.sapellido +' ' + empleado.pnombre + ' ' + empleado.snombre + ' CC: ' + str(empleado.docidentidad) ,  #* esto es el nombre del empleado con su cedula  
        'TipoNomina':contrato.tiponomina , 
        'Cargo':contrato.cargo , 
        'LugarTrabajo': 'falta', #! validar de donde viene la informacion 
        'FechaInicial': contrato.fechafincontrato,
        'EstadoContrato': "Activo" if contrato.estadocontrato == 1 else "Inactivo", 
        'TipoContrato':contrato.tipocontrato.tipocontrato, 
        'MotivoRetiro':contrato.motivoretiro, 
        'ModeloContrato':contrato.idmodelo.tipocontrato, 
        ## compensacion 
        'Salario':"{:,.0f}".format(contrato.salario).replace(',', '.') , 
        'TipoSalario':contrato.tiposalario,
        'ModalidadSalario':contrato.tiposalario, #! modalidad falta , buscar db o preguntar 
        'Formapago':contrato.formapago, #! FALTA 
        'BancoCuenta':contrato.bancocuenta,
        'TipoCuenta':contrato.tipocuentanomina,
        'CuentaNomina':contrato.cuentanomina,
        'CentroCostos':contrato.idcosto.nomcosto,
        'SubcentroCostos':contrato.idsubcosto.nomsubcosto,
        ## seguridad social 
        'Eps':contrato.eps,
        'FondoCesantias':contrato.fondocesantias,
        'Pension':contrato.pension,
        'ARL':contrato.centrotrabajo.nombrecentrotrabajo,
        'Sede':contrato.centrotrabajo.nombrecentrotrabajo,
        'TarifaARL':contrato.idsede.nombresede,
        'Caja':contrato.cajacompensacion,
        'Tipocotizante':contrato.tipocotizante, #! FALTA 
        'Subtipocotizante':contrato.subtipocotizante,
        'Pensionado':contrato.pensionado, #! MODIFCIAR 
        
    }
    
    
    return render(request, './companies/EditContractVisual.html',{'diccontract':DicContract})
