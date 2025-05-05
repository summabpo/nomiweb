
from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Centrotrabajo , Empresa 
from apps.components.decorators import custom_login_required ,custom_permission
from apps.companies.forms.workplaceForm import workplaceForm
from django.contrib import messages

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
@role_required('company')
def workplace(request): 
    """
    Vista para mostrar los centros de trabajo asociados a una empresa y un formulario para crear nuevos centros.

    Esta vista permite a los usuarios autenticados con el rol 'company' ver los centros de trabajo de la empresa 
    y acceder a un formulario para crear nuevos centros de trabajo. Muestra una lista de centros de trabajo existentes 
    y un formulario vacío para ingresar los detalles de un nuevo centro de trabajo.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los datos necesarios para renderizar la vista, como la sesión de usuario.
    
    Returns
    -------
    HttpResponse
        Devuelve la plantilla 'companies/workplace.html' con la lista de centros de trabajo y el formulario para crear uno nuevo.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol 'company'. La vista muestra los centros de trabajo asociados 
    con la empresa del usuario y proporciona una interfaz para crear nuevos centros de trabajo.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    centrotrabajos = Centrotrabajo.objects.filter(id_empresa_id = idempresa ).order_by('centrotrabajo')
    form = workplaceForm()
    
    return render(request, './companies/workplace.html',
                    {
                        'centrotrabajos':centrotrabajos,
                        'form':form,
                    })
    
    
@login_required
@role_required('company')
def workplace_modal(request):
    """
    Vista para crear un nuevo centro de trabajo mediante un formulario en un modal.

    Esta vista maneja el formulario de creación de un nuevo centro de trabajo. Si el método de solicitud es POST 
    y el formulario es válido, se guarda el nuevo centro de trabajo asociado a la empresa del usuario y se devuelve 
    una respuesta JSON indicando el éxito de la operación. En caso de que el formulario sea inválido, se muestran 
    los errores correspondientes.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los datos enviados en el formulario, si es un POST.
    
    Returns
    -------
    HttpResponse
        Si la operación es exitosa, se devuelve un JsonResponse con un mensaje de éxito. 
        Si el formulario es inválido, se procesan los errores y se vuelve a renderizar el formulario.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol 'company'. La vista utiliza un formulario 
    de creación de centro de trabajo (`workplaceForm`), y al ser válido, guarda un nuevo registro en la base de datos.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    if request.method == 'POST':
        form = workplaceForm(request.POST)
        if form.is_valid():
            empresa = Empresa.objects.get(idempresa=usuario['idempresa'])
            nuevo_centro_trabajo = Centrotrabajo(
                nombrecentrotrabajo=form.cleaned_data['nombrecentrotrabajo'] ,
                tarifaarl = form.cleaned_data['tarifaarl'] ,
                id_empresa = empresa
            )
            nuevo_centro_trabajo.save()
            return JsonResponse({'status': 'success', 'message': 'Centro de Trabajo creado exitosamente'})
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
    else:
        form = workplaceForm()    
    return render(request, './companies/partials/workplaceModal.html',
                    {
                        'form':form,
                    })
