from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Tipodocumento,Paises,Ciudades,Contratosemp,Profesiones,Contratos,Centrotrabajo
from apps.companies.forms.ContractForm  import ContractForm 
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
    # for field in contrato._meta.fields:
    #     field_name = field.name
    #     field_value = getattr(contrato, field_name)
    #     print(f"{field_name}: {field_value}")
    
    DicContract = {
        #Contrato
        'Idcontrato':contrato.idcontrato , 
        'FechaTerminacion':contrato.fechainiciocontrato, 
        'Empleado':  empleado.papellido +' ' + empleado.sapellido +' ' + empleado.pnombre + ' ' + empleado.snombre + ' CC: ' + str(empleado.docidentidad) ,  #* esto es el nombre del empleado con su cedula  
        'TipoNomina':contrato.tiponomina , 
        'Cargo':contrato.cargo , 
        'LugarTrabajo': contrato.ciudadcontratacion.idciudad, #* ok  
        'FechaInicial': contrato.fechainiciocontrato,
        'EstadoContrato': "Activo" if contrato.estadocontrato == 1 else "Inactivo", 
        # The line ` 'ModeloContrato':contrato.idmodelo.tipocontrato, ` is accessing the
        # `tipocontrato` attribute of the `idmodelo` object associated with the `contrato` object.
        'TipoContrato':contrato.tipocontrato.idtipocontrato, 
        'MotivoRetiro':contrato.motivoretiro, 
        'ModeloContrato':contrato.idmodelo.tipocontrato, 
        ## compensacion 
        'Salario':"{:,.0f}".format(contrato.salario).replace(',', '.') , 
        'TipoSalario':contrato.tiposalario.idtiposalario,
        'ModalidadSalario':contrato.salariovariable, #* ok 
        'Formapago':  contrato.formapago, #* ok  
        'BancoCuenta':contrato.bancocuenta,
        'TipoCuenta':contrato.tipocuentanomina,
        'CuentaNomina':contrato.cuentanomina,
        'CentroCostos':contrato.idcosto.idcosto,
        'SubcentroCostos':contrato.idsubcosto.idsubcosto,
        ## seguridad social 
        'Eps':contrato.codeps,
        'FondoCesantias':contrato.codccf,
        'Pension':contrato.codafp,
        'ARL':contrato.centrotrabajo.centrotrabajo,
        'Sede':contrato.idsede.idsede,
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
        initial_data = {'endDate': DicContract['FechaTerminacion'] ,
                        'payrollType': DicContract['TipoNomina'] ,
                        'position': DicContract['Cargo'] ,
                        'workLocation': DicContract['LugarTrabajo'] ,
                        'contractStartDate': str(DicContract['FechaInicial']) ,
                        'contractType': DicContract['TipoContrato'] ,
                        'contractModel': DicContract['ModeloContrato'] ,
                        'salary': DicContract['Salario'] ,
                        'salaryType': DicContract['TipoSalario'] ,
                        'paymentMethod': DicContract['Formapago'] ,
                        'salaryMode': DicContract['ModalidadSalario'] ,
                        'bankAccount': DicContract['BancoCuenta'] ,
                        'accountType': DicContract['TipoCuenta'] ,
                        'payrollAccount': DicContract['CuentaNomina'] ,
                        'costCenter': DicContract['CentroCostos'] ,
                        'subCostCenter': DicContract['SubcentroCostos'] ,
                        'eps': DicContract['Eps'],
                        'pensionFund': DicContract['Pension'],
                        'CesanFund': DicContract['FondoCesantias'],
                        'arlWorkCenter': DicContract['Sede'],
                        'workPlace': DicContract['ARL'],
                        } 
        
        form = ContractForm(initial=initial_data)    
        form.fields['endDate'].widget.attrs['disabled'] = True
        form.fields['payrollType'].widget.attrs['disabled'] = True
        form.fields['position'].widget.attrs['disabled'] = True
        form.fields['workLocation'].widget.attrs['disabled'] = True
        form.fields['contractStartDate'].widget.attrs['disabled'] = True
        form.fields['contractType'].widget.attrs['disabled'] = True
        form.fields['contractModel'].widget.attrs['disabled'] = True
        form.fields['salary'].widget.attrs['disabled'] = True
        form.fields['salaryType'].widget.attrs['disabled'] = True
        form.fields['salaryMode'].widget.attrs['disabled'] = True
        form.fields['eps'].widget.attrs['disabled'] = True
        form.fields['pensionFund'].widget.attrs['disabled'] = True
        form.fields['CesanFund'].widget.attrs['disabled'] = True
        form.fields['arlWorkCenter'].widget.attrs['disabled'] = True
        form.fields['workPlace'].widget.attrs['disabled'] = True
    
    return render(request, './companies/EditContractVisual.html',{'form':form,'contrato':contrato , 'DicContract':DicContract})
