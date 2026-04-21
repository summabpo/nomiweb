from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models import Costos,Empresa 
from apps.components.decorators import custom_login_required ,custom_permission
from apps.companies.forms.CostcenterForm import CostcenterForm
from django.contrib import messages

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required
@role_required('company','accountant')
def Costcenter(request): 
    """
    Muestra los centros de costos asociados a una empresa.

    Esta vista permite visualizar todos los centros de costos asociados a una empresa en particular. 
    Los centros de costos que tienen un grupo contable y sufijo diferente a 0 son incluidos en la lista.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los datos del usuario en sesión.
        - 'usuario' es un diccionario con información de la sesión, incluyendo 'idempresa'.

    Returns
    -------
    HttpResponse
        Devuelve una página HTML que muestra la lista de centros de costos y el formulario 
        para crear un nuevo centro de costo.

    See Also
    --------
    Costos : Modelo que representa los datos de los centros de costos.
    CostcenterForm : Formulario utilizado para la creación de un nuevo centro de costo.
    role_required : Decorador personalizado que restringe el acceso según el rol.
    login_required : Decorador de Django que exige autenticación del usuario.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol `'company'` para acceder a esta vista.
    """
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    costos = Costos.objects.filter(id_empresa__idempresa=usuario['idempresa'] ).exclude(grupocontable= 0 ,suficosto = 0 ).order_by('idcosto')
    form = CostcenterForm(idempresa = idempresa)
    
    return render(request, './companies/costcenter.html',
                    {
                        'costos':costos,
                        'form':form,
                    })



@login_required
@role_required('company','accountant')
def costcenter_modal(request): 
    
    """
    Muestra el modal para crear un nuevo centro de costo.

    Esta vista maneja la creación de un nuevo centro de costo a través de un formulario en un modal. 
    Si se realiza una solicitud POST con datos válidos, crea un nuevo centro de costo y responde en formato JSON.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los datos del formulario a procesar.

    Returns
    -------
    JsonResponse
        Si el formulario es válido, devuelve una respuesta JSON con un mensaje de éxito.
    HttpResponse
        Si la solicitud no es POST, muestra el formulario vacío en un modal.

    See Also
    --------
    CostcenterForm : Formulario utilizado para la creación de un nuevo centro de costo.
    Costos : Modelo que representa los datos de los centros de costos.
    role_required : Decorador personalizado que restringe el acceso según el rol.
    login_required : Decorador de Django que exige autenticación del usuario.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol `'company'` para acceder a esta vista.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    if request.method == 'POST':
        form = CostcenterForm(request.POST, idempresa = idempresa)
        if form.is_valid():
            empresa = Empresa.objects.get(idempresa=usuario['idempresa'])
            nuevo_costo = Costos(
                nomcosto=form.cleaned_data['nomcosto'],
                suficosto=form.cleaned_data['suficosto'],
                grupocontable=form.cleaned_data['grupocontable'],
                id_empresa = empresa
            )
            nuevo_costo.save()
            return JsonResponse({'status': 'success', 'message': 'Centro de Costo creado exitosamente'})
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
    else:
        form = CostcenterForm(idempresa = idempresa)    
    return render(request, './companies/partials/costcenterModal.html',
                    {
                        'form':form,
                    })