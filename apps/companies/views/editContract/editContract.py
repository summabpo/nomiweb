from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.models import Contratosemp,Contratos, Costos ,Subcostos,Centrotrabajo
from apps.companies.forms.ContractForm import ContractForm 
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


def EditContracVisual(request,idempleado):
    empleado = Contratosemp.objects.using("lectaen").get(idempleado=idempleado) 
    contrato = get_object_or_404(Contratos, idempleado=idempleado,estadocontrato=1)
    
    DicContract = {
        'Idcontrato': contrato.idcontrato,
        'FechaTerminacion': str(contrato.fechafincontrato),
        'Empleado': empleado.papellido + ' ' + empleado.sapellido + ' ' + empleado.pnombre + ' ' + empleado.snombre + ' CC: ' + str(empleado.docidentidad),
        'TipoNomina': contrato.tiponomina,
        'Cargo': contrato.cargo,
        'LugarTrabajo': contrato.ciudadcontratacion.idciudad,
        'FechaInicial': contrato.fechainiciocontrato,
        'EstadoContrato': "Activo" if contrato.estadocontrato == 1 else "Inactivo",
        'TipoContrato': contrato.tipocontrato.idtipocontrato,
        'MotivoRetiro': contrato.motivoretiro,
        'ModeloContrato': contrato.idmodelo.tipocontrato,
        'Salario': contrato.salario,
        'TipoSalario': contrato.tiposalario.idtiposalario,
        'ModalidadSalario': contrato.salariovariable,
        'Formapago': contrato.formapago,
        'BancoCuenta': contrato.bancocuenta,
        'TipoCuenta': contrato.tipocuentanomina,
        'CuentaNomina': contrato.cuentanomina,
        'CentroCostos': contrato.idcosto.idcosto,
        'SubcentroCostos': contrato.idsubcosto.idsubcosto,
        'Eps': contrato.codeps,
        'FondoCesantias': contrato.codccf,
        'Pension': contrato.codafp,
        'ARL': contrato.centrotrabajo.centrotrabajo,
        'Sede': contrato.idsede.idsede,
        'TarifaARL': contrato.idsede.nombresede,
        'Caja': contrato.cajacompensacion,
        'Tipocotizante': contrato.tipocotizante,
        'Subtipocotizante': contrato.subtipocotizante,
        'Pensionado': contrato.pensionado,
    }
    
    initial_data = {
        'endDate': str(contrato.fechafincontrato),
        'payrollType': contrato.tiponomina,
        'position': contrato.cargo,
        'workLocation': contrato.ciudadcontratacion.idciudad,
        'contractStartDate': str(contrato.fechainiciocontrato),
        'contractType': contrato.tipocontrato.idtipocontrato,
        'contractModel': contrato.idmodelo.idmodelo,
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
            try:
                contrato.tiponomina =form.cleaned_data['payrollType']
                contrato.bancocuenta =form.cleaned_data['bankAccount']
                contrato.cuentanomina =form.cleaned_data['payrollAccount']
                contrato.tipocuentanomina =form.cleaned_data['accountType']
                contrato.formapago =form.cleaned_data['paymentMethod']
                contrato.idcosto =Costos.objects.get( idcosto =  form.cleaned_data['costCenter'] )  
                contrato.idsubcosto =Subcostos.objects.get( idsubcosto =  form.cleaned_data['subCostCenter'] )
                contrato.save()
                messages.success(request, 'El Contrato ha sido Actualizado')
                return  redirect('companies:editcontracsearch')
            except Exception as e:
                print(e)
                messages_error = 'Se produjo un error al guardar el Contrato.' + str(e.args)
                messages.error(request, messages_error)
                return redirect('companies:editcontracvisual',idempleado=empleado.idempleado)
        else:       
            premium = request.GET.get('premium', False)
            form = ContractForm(initial=initial_data) 
            form.set_premium_fields(premium=premium) 
    else:
        premium = request.GET.get('premium', False)
        
        form = ContractForm(initial=initial_data) 
        form.set_premium_fields(premium=premium) 
        
    return render(request, './companies/EditContractVisual.html',{'form':form,'contrato':contrato , 'DicContract':DicContract})
