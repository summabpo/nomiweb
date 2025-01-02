from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Contratosemp,Contratos, Costos ,Subcostos,Centrotrabajo
from .EditForm import ContractForm 
from django.contrib import messages

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('company','accountant')
def EditContracVisual(request,idempleado):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    empleado = Contratosemp.objects.get(idempleado=int(idempleado)) 
    contrato = Contratos.objects.get(idempleado=idempleado, estadocontrato=1)
    
    DicContract = {
        'Idcontrato': contrato.idcontrato,
        'Empleado': (contrato.idempleado.papellido or '')  + ' ' + (contrato.idempleado.sapellido or '' ) + ' ' + (contrato.idempleado.pnombre or '') + ' ' + (contrato.idempleado.snombre or '') + ' CC: ' + str(contrato.idempleado.docidentidad),
        'EstadoContrato': "Activo" if contrato.estadocontrato == 1 else "Inactivo",
    }
    
    initial_data = {
        'name' : contrato.idempleado.idempleado , 
        'endDate': str(contrato.fechafincontrato),
        'payrollType': contrato.tiponomina.idtiponomina,
        'position': contrato.cargo.idcargo,
        'workLocation': contrato.ciudadcontratacion.idciudad,
        'contractStartDate': str(contrato.fechainiciocontrato),
        'contractType': contrato.tipocontrato.idtipocontrato,
        'contractModel': contrato.idmodelo.idmodelo,
        'salary': "{:,.0f}".format(contrato.salario).replace(',', '.'),
        'salaryType': contrato.tiposalario.idtiposalario,
        'paymentMethod': contrato.formapago,
        'salaryMode': contrato.salariovariable,
        'bankAccount': contrato.bancocuenta.idbanco,
        'accountType': contrato.tipocuentanomina,
        'payrollAccount': contrato.cuentanomina,
        'costCenter': contrato.idcosto.idcosto,
        'subCostCenter': contrato.idsubcosto.idsubcosto if contrato.idsubcosto else '',
        'eps': contrato.codeps.identidad,
        'pensionFund': contrato.codafp.identidad,
        'CesanFund': contrato.codccf.identidad,
        'arlWorkCenter': contrato.centrotrabajo.centrotrabajo,
        'workPlace': contrato.idsede.idsede,
    }

    
    if request.method == 'POST':
        form = ContractForm(request.POST,idempresa=idempresa)


        if form.is_valid():
            print(request.POST)
            try:

                # Solo se realiza el cambio si el valor no es None ni vacío
                if form.cleaned_data['payrollType'] not in ('', None):
                    contrato.tiponomina_id = form.cleaned_data['payrollType']

                if form.cleaned_data['bankAccount'] not in ('', None):
                    contrato.bancocuenta_id = form.cleaned_data['bankAccount']

                if form.cleaned_data['payrollAccount'] not in ('', None):
                    contrato.cuentanomina = form.cleaned_data['payrollAccount']

                if form.cleaned_data['accountType'] not in ('', None):
                    contrato.tipocuentanomina = form.cleaned_data['accountType']

                if form.cleaned_data['paymentMethod'] not in ('', None):
                    contrato.formapago = form.cleaned_data['paymentMethod']

                if form.cleaned_data['costCenter'] not in ('', None):
                    contrato.idcosto = Costos.objects.get(idcosto=form.cleaned_data['costCenter'])

                print(form.cleaned_data['subCostCenter'])
                if form.cleaned_data['subCostCenter'] not in ('', None):
                    contrato.idsubcosto = Subcostos.objects.get(idsubcosto=form.cleaned_data['subCostCenter'])

                contrato.save()
                messages.success(request, 'El Contrato ha sido Actualizado')
                return  redirect('companies:startcompanies')
            except Exception as e:
                print(e)
                messages_error = 'Se produjo un error al guardar el Contrato.' + str(e.args)
                messages.error(request, messages_error)
                return redirect('companies:editcontracvisual',idempleado=empleado.idempleado)
        else: 
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo '{field}': {error}")
            messages.error(request,'Todo lo que podía fallar, falló.')
            return redirect('companies:editcontracvisual',idempleado=empleado.idempleado)
    else:
        form = ContractForm(idempresa=idempresa ,initial=initial_data)

        
    return render(request, './companies/EditContractVisual.html',{'form':form,'contrato':contrato ,'user': request.user, 'DicContract':DicContract})
