from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Tipodocumento ,ModelosContratos,Tiposalario, Paises ,Subcostos,Costos, Ciudades ,Contratosemp, Profesiones,Contratos ,Tipocontrato , Centrotrabajo,Sedes
from apps.companies.forms.ContractForm  import ContractForm 
from django.contrib import messages
from apps.components.decorators import custom_login_required ,custom_permission


from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('company')
def newContractVisual(request):   
    empleados = Contratosemp.objects.filter(estadocontrato=4)
    return render(request, './companies/newContractVisual.html',{'empleados':empleados})


@login_required
@role_required('company')
def newContractCreater(request,idempleado):
    
    empleado = get_object_or_404(Contratosemp, idempleado=idempleado)
    if request.method == 'POST':
        try:
            form = ContractForm(request.POST)            
            if form.is_valid():
                contratos_instance = Contratos(
                    cargo =form.cleaned_data['position'],
                    fechainiciocontrato =form.cleaned_data['contractStartDate'],
                    fechafincontrato =form.cleaned_data['endDate'],
                    tipocontrato = Tipocontrato.objects.get(idtipocontrato=form.cleaned_data['contractType'])  ,
                    tiponomina =form.cleaned_data['payrollType'],
                    bancocuenta =form.cleaned_data['bankAccount'],
                    cuentanomina =form.cleaned_data['payrollAccount'],
                    tipocuentanomina =form.cleaned_data['accountType'],
                    #! modificar para que guarde le nombre basado en la db 
                    eps =form.cleaned_data['eps'],                
                    pension =form.cleaned_data['pensionFund'],
                    cajacompensacion =form.cleaned_data['accountType'],
                    #! modificar para que guarde le nombre basado en la db 
                    
                    tarifaarl ='0',
                    ciudadcontratacion = Ciudades.objects.get( idciudad =  form.cleaned_data['workLocation']) ,
                    fondocesantias =form.cleaned_data['CesanFund'],
                    estadocontrato  = 1,
                    salario = form.cleaned_data['salary'],
                    idempleado = Contratosemp.objects.get( idempleado = idempleado) ,
                    tipocotizante = '' ,
                    subtipocotizante = '',
                    formapago  = form.cleaned_data['paymentMethod'],
                    metodoretefuente = '' ,
                    porcentajeretefuente =0,
                    valordeduciblevivienda =0,
                    saludretefuente = 0,
                    pensionado  = '2',
                    estadoliquidacion = 1,
                    estadosegsocial = 0,
                    motivoretiro = '',
                    tiposalario = Tiposalario.objects.get( idtiposalario =  form.cleaned_data['salaryType'] )  ,
                    idcosto  =  Costos.objects.get( idcosto =  form.cleaned_data['costCenter'] )  ,
                    idsubcosto   = Subcostos.objects.get( idsubcosto =  form.cleaned_data['subCostCenter'] )   ,
                    idsede = Sedes.objects.get( idsede =   form.cleaned_data['workPlace'] ) ,
                    salariovariable  = form.cleaned_data['salaryMode'],
                    
                    codeps  = form.cleaned_data['eps'],
                    codafp  = form.cleaned_data['pensionFund'],
                    codccf  = form.cleaned_data['CesanFund'],
                    
                    #! requiere un condicional 
                    auxiliotransporte = 0,
                    
                    #! se requiere informacion 
                    
                    dependientes = 0,
                    valordeduciblemedicina = 0,
                    jornada = '',
                    idmodelo = ModelosContratos.objects.get( idmodelo = form.cleaned_data['contractModel'])  ,
                    coddepartamento ='0',
                    codciudad = '0',
                    riesgo_pension = '0',

                )
                contratos_instance.save()
                empleado.estadocontrato = 1
                empleado.save()
                messages.success(request, 'El Contrato ha sido creado')
                return  redirect('companies:newcontractvisual')
            
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en el campo '{field}': {error}")
                return redirect('companies:newemployee')
            
        except Exception as e:
            print(e)
            messages_error = 'Se produjo un error al guardar el Contrato.' + str(e.args)
            messages.error(request, messages_error)
            return redirect('companies:newemployee')

    else:
        form = ContractForm      
        
    return render(request, './companies/newContractCreate.html',{'form':form})


