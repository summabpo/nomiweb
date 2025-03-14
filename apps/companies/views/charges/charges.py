from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Cargos,Empresa,Nivelesestructura
from apps.components.decorators import custom_login_required ,custom_permission
from apps.companies.forms.chargesForm import ChargesForm
from django.contrib import messages
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django.shortcuts import get_object_or_404

def toggle_charge_active_status(request, id, activate=True):
    cargo = get_object_or_404(Cargos, idcargo = id)
    cargo.estado = activate
    cargo.save()
    status_message = 'activado' if activate else 'desactivado'
    messages.success(request, f'El Cargo ha sido {status_message} con éxito.')
    return redirect('companies:charges')

@login_required
@role_required('company','accountant')
def charges(request): 
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    cargos = Cargos.objects.filter(id_empresa__idempresa=usuario['idempresa']).exclude(idcargo=241).order_by('idcargo')
    form = ChargesForm(idempresa = idempresa)
    return render(request, './companies/charges.html',
                    {
                        'cargos':cargos,
                        'form':form,
                    })
    
    
@login_required
@role_required('company','accountant')
def charges_modal(request): 
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    if request.method == 'POST':
        form = ChargesForm(request.POST, idempresa = idempresa)
        if form.is_valid():
            empresa = Empresa.objects.get(idempresa=usuario['idempresa'])
            nivel = Nivelesestructura.objects.get( idnivel = form.cleaned_data['nivelcargo'] )
            nuevo_cargo = Cargos(
                nombrecargo=form.cleaned_data['nombrecargo'] ,
                nombrenivel = nivel,
                id_empresa = empresa
            )
            nuevo_cargo.save()
            return JsonResponse({'status': 'success', 'message': 'Cargo creado exitosamente'})
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
    else:
        form = ChargesForm(idempresa = idempresa)    
    return render(request, './companies/partials/chargeModal.html',
                    {
                        'form':form,
                    })
    
