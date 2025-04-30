from django.shortcuts import render ,redirect
from apps.employees.forms.newpasswordform import CustomPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required





@login_required
@role_required('employee')
def newpassword_employees(request):
    
    """
    Permite al empleado cambiar su contraseña.

    Esta vista proporciona un formulario que permite a los empleados cambiar su contraseña. Se utiliza el formulario `CustomPasswordChangeForm`, que valida la nueva contraseña y actualiza los datos del usuario en la base de datos.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP que contiene la información de la sesión del usuario y los datos del formulario.

    Returns
    -------
    HttpResponse
        Si el formulario es válido, redirige al usuario a su perfil con un mensaje de éxito.
        Si hay errores de validación, renderiza nuevamente la página con los mensajes de error.

    Notes
    -----
    - Solo accesible para empleados autenticados.
    - Requiere que el usuario complete el formulario para cambiar su contraseña.
    - Después de cambiar la contraseña, la sesión del usuario se actualiza para reflejar los cambios.
    - Si hay algún error de validación, se mostrará un mensaje de error para que el usuario pueda corregirlo.
    """

    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) 
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
            return redirect('employees:user')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, './employees/newpassword.html',{'form':form})
    
    





