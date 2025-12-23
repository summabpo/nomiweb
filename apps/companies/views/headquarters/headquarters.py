
from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Sedes ,Entidadessegsocial
from apps.components.decorators import custom_login_required ,custom_permission
from apps.companies.forms.headquartersForm import headquartersForm
from django.contrib import messages
from django.db import transaction

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


"""
    Funciones para manejar las sedes de una empresa.

    Estas funciones permiten al usuario gestionar las sedes de la empresa, visualizando y creando sedes
    mediante formularios y consultas a la base de datos. Las vistas están protegidas por autenticación
    y roles de usuario, asegurando que solo los usuarios con el rol adecuado puedan acceder a las funcionalidades.

    Funciones
    ---------
    headquarters(request)
        Vista para mostrar el listado de sedes asociadas a la empresa y un formulario para crear una nueva sede.

    headquarters_modal(request)
        Vista para crear una nueva sede desde un modal (formulario emergente) y guardar los datos en la base de datos.
        
    Descripción
    -----------
    Ambas vistas están protegidas por el decorador `login_required` y `role_required('company')`, lo que
    asegura que solo los usuarios autenticados con el rol 'company' puedan acceder a ellas.

    Parámetros
    ----------
    request : HttpRequest
        El objeto de la solicitud HTTP recibido por la vista. Contiene información sobre el usuario y el formulario.

    Retorna
    -------
    - En la función `headquarters`: un renderizado de la plantilla `headquarters.html` que incluye el listado
      de sedes de la empresa y un formulario vacío para crear una nueva sede.
      
    - En la función `headquarters_modal`: un renderizado de la plantilla `headquartersModal.html` con el formulario
      para crear una nueva sede. Si el formulario es válido, se guarda la nueva sede en la base de datos y se
      retorna un `JsonResponse` indicando el éxito de la operación.

    Notas
    -----
    - La función `headquarters` consulta las sedes asociadas a la empresa del usuario actual, excluyendo la sede
      con `idsede=16` y ordenando las sedes por `idsede`.
    - La función `headquarters_modal` permite crear una sede nueva. Al recibir una solicitud POST con los datos
      del formulario, se valida y guarda la sede, asociándola a la empresa del usuario actual y a una entidad de
      seguridad social obtenida mediante un código de compensación proporcionado.
"""

@login_required
@role_required('company')
def headquarters(request): 
    """
    Vista que muestra un listado de las sedes de la empresa del usuario autenticado y un formulario para crear nuevas sedes.
    
    Parámetros:
    -----------
    request : HttpRequest
        Objeto que contiene la información de la solicitud HTTP.

    Retorna:
    --------
    - Renderiza la plantilla 'headquarters.html' con las sedes de la empresa y un formulario vacío para crear nuevas sedes.
    """


    usuario = request.session.get('usuario', {})
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    sedes = Sedes.objects.filter(id_empresa_id = idempresa).exclude(idsede=16).order_by('idsede')
    form = headquartersForm()
    return render(request, './companies/headquarters.html',
                    {
                        'sedes':sedes,
                        'form':form,
                    })
    
    
    
    

@login_required
@role_required('company')
def headquarters_modal(request): 
    """
    Vista para crear una nueva sede desde un modal. El formulario permite ingresar los datos necesarios
    y, si es válido, crea una nueva sede asociada a la empresa del usuario autenticado.

    Parámetros:
    -----------
    request : HttpRequest
        Objeto que contiene la información de la solicitud HTTP.

    Retorna:
    --------
    - Si la solicitud es GET, renderiza el formulario en un modal.
    - Si la solicitud es POST, valida el formulario y crea una nueva sede, luego devuelve un `JsonResponse` con el resultado.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    print('-------------')
    print('prueba')
    print('-------------')
    
    if request.method == 'POST':
        form = headquartersForm(request.POST)
        if form.is_valid():
            
            print('-------------')
            print('prueba')
            print('-------------')
            nombresede = form.cleaned_data['nombresede']
            cajacompensacion = form.cleaned_data['cajacompensacion']
            aux = Entidadessegsocial.objects.get(codigo=cajacompensacion)
            sede = Sedes(
                nombresede=nombresede,
                cajacompensacion=aux.entidad,
                codccf=aux.codigo,
                id_empresa_id = idempresa
            )
            sede.save()
            
            print(sede)
            return JsonResponse({'status': 'success', 'message': 'Sede creada exitosamente'})
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
    else:
        form = headquartersForm()    
    return render(request, './companies/partials/headquartersModal.html',
                    {
                        'form':form,
                    })