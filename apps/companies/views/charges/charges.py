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
    """
    Muestra la lista de cargos en la empresa.

    Esta vista recupera y muestra todos los cargos activos de la empresa a la que el usuario pertenece,
    excluyendo un cargo con un ID específico. También proporciona un formulario para la creación de nuevos cargos.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene la sesión del usuario.

    Returns
    -------
    render : HttpResponse
        Respuesta con la vista de los cargos y el formulario para crear nuevos cargos.

    See Also
    --------
    Cargos : Modelo que representa los cargos en la empresa.
    ChargesForm : Formulario utilizado para la creación de nuevos cargos.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol `'company'` o `'accountant'` para acceder a esta vista.
    """

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
    """
    Muestra y maneja el formulario modal para la creación de un nuevo cargo.

    Esta vista maneja el formulario para la creación de un nuevo cargo en la empresa. Si el formulario es
    válido, crea un nuevo cargo y lo guarda en la base de datos. Si el formulario no es válido, muestra los errores
    correspondientes.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los datos del formulario.

    Returns
    -------
    render : HttpResponse
        Respuesta con el formulario de creación de cargo en un modal. Si el formulario es válido, se retorna
        un objeto JSON con el estado de éxito. Si no, se muestra el formulario con errores.

    See Also
    --------
    Cargos : Modelo que representa los cargos en la empresa.
    ChargesForm : Formulario utilizado para la creación de nuevos cargos.
    Empresa : Modelo que representa la empresa.
    Nivelesestructura : Modelo que representa los niveles de la estructura organizativa de la empresa.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol `'company'` o `'accountant'` para acceder a esta vista.
    """

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
    



