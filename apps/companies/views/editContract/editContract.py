from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Contratosemp,Contratos, Costos ,Subcostos,Centrotrabajo
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
<<<<<<< HEAD
    
=======
>>>>>>> 50cc76f7567e2fe93c850b7bb7f51acb6a0fcc19
    contrato = get_object_or_404(Contratos, idempleado=idempleado,estadocontrato=1)
    # Definición de DicContract con las variables que se usarán en el HTML
    DicContract = {
        'Idcontrato': contrato.idcontrato,
        'FechaTerminacion': contrato.fechafincontrato,
        'Empleado':  empleado.papellido + ' ' + empleado.sapellido + ' ' + empleado.pnombre + ' ' + empleado.snombre + ' CC: ' + str(empleado.docidentidad),
        'EstadoContrato': "Activo" if contrato.estadocontrato == 1 else "Inactivo",
        'MotivoRetiro': contrato.motivoretiro,
        'TarifaARL': contrato.idsede.nombresede,
        'Caja': contrato.cajacompensacion,
        'Tipocotizante': contrato.tipocotizante,
        'Subtipocotizante': contrato.subtipocotizante,
        'Pensionado': contrato.pensionado,
    }
    
    # Definición de initial_data con las variables que se usarán en el formulario
    initial_data = {
        'endDate': str(contrato.fechafincontrato),
        'payrollType': contrato.tiponomina,
        'position': contrato.cargo,
        'workLocation': contrato.ciudadcontratacion.idciudad,
        'contractStartDate': str(contrato.fechainiciocontrato),
        'contractType': contrato.tipocontrato.idtipocontrato,
        'contractModel': contrato.idmodelo.tipocontrato,
        'salary': "{:,.0f}".format(contrato.salario).replace(',', '.'),
        'salaryType': contrato.tiposalario.idtiposalario,
        'paymentMethod': contrato.formapago,
        'salaryMode': contrato.salariovariable,
        'bankAccount': contrato.bancocuenta,
        'accountType': contrato.tipocuentanomina,
        'payrollAccount': contrato.cuentanomina,
        'costCenter': contrato.idcosto.idcosto,
        'subCostCenter': contrato.idsubcosto.idsubcosto,
        'eps': contrato.codeps,
        'pensionFund': contrato.codafp,
        'CesanFund': contrato.codccf,
        'arlWorkCenter': contrato.centrotrabajo.centrotrabajo,
        'workPlace': contrato.idsede.idsede,
    }

    
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            
            """ 
            'paymentMethod',
            'bankAccount',
            'accountType',
            'payrollAccount',
            'costCenter',
            'subCostCenter'
            
            """
            
            contratos_instance = Contratos(
                    tiponomina =form.cleaned_data['payrollType'],
                    bancocuenta =form.cleaned_data['bankAccount'],#*
                    cuentanomina =form.cleaned_data['payrollAccount'],#*
                    tipocuentanomina =form.cleaned_data['accountType'],#*
                    formapago  = form.cleaned_data['paymentMethod'],#*
                    idcosto  =  Costos.objects.get( idcosto =  form.cleaned_data['costCenter'] )  ,#*
                    idsubcosto   = Subcostos.objects.get( idsubcosto =  form.cleaned_data['subCostCenter'] ), #*  ,
                    
                    #todo : No editables 
                    centrotrabajo = Centrotrabajo.objects.get(centrotrabajo =  form.cleaned_data['arlWorkCenter'] )  ,
                    

                )
            contratos_instance.save()
            messages.success(request, 'El Contrato ha sido Actualizado')
            return  redirect('companies:editcontracsearch')
            # try:
                
            # except Exception as e:
            #     print(e)
            #     messages_error = 'Se produjo un error al guardar el Contrato.' + str(e.args)
            #     messages.error(request, messages_error)
            #     return redirect('companies:editcontracvisual',idempleado=empleado.idempleado)
        # else:
        #     for field, errors in form.errors.items():
        #         for error in errors:
        #             messages.error(request, f"Error en el campo '{field}': {error}")
        #     return redirect('companies:editcontracvisual',idempleado=empleado.idempleado)
    else:
        
        
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
