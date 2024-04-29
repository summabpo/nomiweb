from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento,Paises,Ciudades,Contratosemp,Profesiones,Contratos,Centrotrabajo
from apps.companies.forms.ContractFormedit import ContractForm
from django.contrib import messages



def EditContracsearch(request):
    contratos_empleados = Contratos.objects.using("lectaen") \
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .filter(estadocontrato=1) \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__sapellido','idempleado__pnombre',
                'idempleado__snombre', 'fechainiciocontrato', 'cargo', 'idempleado__direccionempleado',
                'ciudadcontratacion__ciudad','idempleado__celular','idempleado__email','idempleado__idempleado')

    empleados = []
    for contrato in contratos_empleados:
        nombre_empleado = f"{contrato['idempleado__papellido']} {contrato['idempleado__sapellido']}  {contrato['idempleado__pnombre']} {contrato['idempleado__snombre']}"
        contrato_data = {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': nombre_empleado,
            'fechainiciocontrato': contrato['fechainiciocontrato'],
            'cargo': contrato['cargo'],
            'dirección': contrato['idempleado__direccionempleado'],
            'ciudad': contrato['ciudadcontratacion__ciudad'],
            'celular': contrato['idempleado__celular'],
            'mail': contrato['idempleado__email'],
            'id':contrato['idempleado__idempleado'],
        }

        empleados.append(contrato_data)
    
    
    
    
    return render(request, './companies/EditContractSearch.html',{'empleados':empleados})


"""  
def EditEmployeeSearch(request):
    contratos_empleados = Contratos.objects.using("lectaen") \
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .filter(estadocontrato=1) \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__sapellido','idempleado__pnombre',
                'idempleado__snombre', 'fechainiciocontrato', 'cargo', 'idempleado__direccionempleado',
                'ciudadcontratacion__ciudad','idempleado__celular','idempleado__email','idempleado__idempleado')

    empleados = []
    for contrato in contratos_empleados:
        nombre_empleado = f"{contrato['idempleado__papellido']} {contrato['idempleado__sapellido']}  {contrato['idempleado__pnombre']} {contrato['idempleado__snombre']}"
        contrato_data = {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': nombre_empleado,
            'fechainiciocontrato': contrato['fechainiciocontrato'],
            'cargo': contrato['cargo'],
            'dirección': contrato['idempleado__direccionempleado'],
            'ciudad': contrato['ciudadcontratacion__ciudad'],
            'celular': contrato['idempleado__celular'],
            'mail': contrato['idempleado__email'],
            'id':contrato['idempleado__idempleado'],
        }

        empleados.append(contrato_data)
        
    return render(request, './companies/EditEmployeesearch.html', {'empleados': empleados})



"""


def EditContracVisual(request,idempleado):
    empleado = Contratosemp.objects.using("lectaen").get(idempleado=idempleado) 
    contrato = get_object_or_404(Contratos, idempleado=idempleado,estadocontrato=1)

    DicContract = {
        #Contrato
        'Idcontrato':contrato.idcontrato , 
        'FechaTerminacion':contrato.fechafincontrato , 
        'Empleado':  empleado.papellido +' ' + empleado.sapellido +' ' + empleado.pnombre + ' ' + empleado.snombre + ' CC: ' + str(empleado.docidentidad) ,  #* esto es el nombre del empleado con su cedula  
        'TipoNomina':contrato.tiponomina , 
        'Cargo':contrato.cargo , 
        'LugarTrabajo': contrato.ciudadcontratacion, #* ok  
        'FechaInicial': contrato.fechafincontrato,
        'EstadoContrato': "Activo" if contrato.estadocontrato == 1 else "Inactivo", 
        'TipoContrato':contrato.tipocontrato.tipocontrato, 
        'MotivoRetiro':contrato.motivoretiro, 
        'ModeloContrato':contrato.idmodelo.tipocontrato, 
        ## compensacion 
        'Salario':"{:,.0f}".format(contrato.salario).replace(',', '.') , 
        'TipoSalario':contrato.tiposalario.tiposalario,
        'ModalidadSalario':contrato.tiposalario, #* ok 
        'Formapago':  "Abono a Cuenta" if contrato.formapago == '1' else ("Cheque" if contrato.formapago == '2' else "Efectivo"), #* ok  
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
    
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            
            empleado.estadocontrato = 1
            
            empleado.save()
            
            messages.success(request, 'El Contrato ha sido creado')
            
            return  redirect('companies:editcontracsearch')
            # try:
                
            # except Exception as e:
            #     print(e)
            #     messages_error = 'Se produjo un error al guardar el Contrato.' + str(e.args)
            #     messages.error(request, messages_error)
            #     return redirect('companies:newemployee')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo '{field}': {error}")
            return redirect('companies:editcontracvisual')
    else:
        initial_data = {'payrollAccount': 'Nombre existente' , 'payrollType':'Mensual'} 
        form = ContractForm(initial=initial_data)    
        form.fields['payrollType'].widget.attrs['disabled'] = True
        form.fields['payrollAccount'].widget.attrs['disabled'] = True
        
    # POST 
    
    
    # FIN POST 
    
    
    
    return render(request, './companies/EditContractVisual.html',{'form':form,'contrato':DicContract})
