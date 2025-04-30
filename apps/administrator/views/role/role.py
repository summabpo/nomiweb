from django.shortcuts import render,redirect
from apps.administrator.forms.rolesForm import RolesForm
from django.contrib import messages
from apps.common.models import Role




def role_admin(request):
    
    """
    Vista para la administración de roles en la aplicación.

    Esta vista maneja la creación de nuevos roles en el sistema a través de un formulario. Si el formulario 
    es válido, se crea un nuevo rol en la base de datos y se muestra un mensaje de éxito. Si la solicitud 
    es GET, se muestra el formulario vacío para la creación de roles y una lista de los roles existentes.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que puede ser una solicitud GET o POST. En una solicitud POST, se envía un 
        formulario con los datos para crear un nuevo rol.

    Returns
    -------
    HttpResponse
        Respuesta con el formulario de creación de roles y la lista de roles existentes, o redirección a la 
        misma vista después de crear un rol exitosamente, junto con un mensaje de éxito.

    Notes
    -----
    - El formulario para crear un rol se encuentra en `apps.administrator.forms.rolesForm.RolesForm`.
    - Los roles creados se guardan en la tabla `Role` de la base de datos.
    - En el caso de una solicitud POST válida, el rol es creado y se muestra un mensaje de éxito al usuario.
    - En el caso de una solicitud GET, se muestra un formulario vacío para crear un nuevo rol y una lista con 
        los roles existentes.
    """


    if request.method == 'POST':
        form = RolesForm(request.POST)
        if form.is_valid():
            Role.objects.create(
                name=form.cleaned_data['nombre'],
                description = form.cleaned_data['descripcion']
            )
            messages.success(request, 'El Rol Fue creado Correctamente')
            return redirect('admin:role')
    else:
        form = RolesForm()
        roles = Role.objects.all()
        
        
    return render(request, './admin/role.html',{
        'form': form,
        'roles':roles
        
        })