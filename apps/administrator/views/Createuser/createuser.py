from django.shortcuts import render,redirect
from apps.administrator.forms.createuserForm import UserCreationForm , UserEditForm
from django.contrib import messages
from apps.common.models import User,Empresa , Role
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from apps.components.mail import send_template_email
import random
import string
import urllib.parse

def generate_random_password(length=12):
    """
    Genera una contraseña aleatoria segura.

    Combina letras, números y caracteres especiales para crear una contraseña fuerte.

    Parameters
    ----------
    length : int, optional
        Longitud de la contraseña a generar (por defecto 12 caracteres).

    Returns
    -------
    str
        Cadena con la contraseña aleatoria generada.
    """
    
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))


def toggle_user_active_status(request, user_id, activate=True):
    
    """
    Activa o desactiva un usuario del sistema administrativo.

    Este view se utiliza para cambiar el estado `is_active` de un usuario.
    El cambio se refleja inmediatamente y se redirige a la vista principal de usuarios.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP.
    user_id : int
        ID del usuario cuyo estado se desea modificar.
    activate : bool, optional
        Valor booleano para activar (True) o desactivar (False) el usuario. Por defecto es True.

    Returns
    -------
    HttpResponseRedirect
        Redirige a la vista `admin:user` tras actualizar el estado del usuario.

    Raises
    ------
    Http404
        Si no se encuentra el usuario con el `user_id` dado.

    Notes
    -----
    - El cambio de estado afecta directamente la capacidad del usuario de iniciar sesión.
    - Se muestra un mensaje de éxito usando el sistema de mensajes de Django.
    """
    
    
    usuario = get_object_or_404(User, id=user_id)
    usuario.is_active = activate
    usuario.save()
    status_message = 'activado' if activate else 'desactivado'
    messages.success(request, f'El usuario ha sido {status_message} con éxito.')
    return redirect('admin:user')


def user_admin(request):
    
    """
    Muestra la vista principal de gestión de usuarios en el panel administrativo.

    Esta vista lista todos los usuarios registrados y presenta un formulario para crear nuevos usuarios.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla `admin/users.html` con la lista de usuarios y el formulario de creación.

    See Also
    --------
    usercreate_admin : Vista para procesar la creación de usuarios.
    User : Modelo que representa a los usuarios del sistema.
    UserCreationForm : Formulario personalizado para registrar usuarios desde el panel administrativo.
    """
    
    users = User.objects.all().order_by('-id')
    form = UserCreationForm()
    return render(request, './admin/users.html' , {'users':users,'form':form}) 


def usercreate_admin(request):
    
    """
    Procesa la creación de un nuevo usuario desde el panel administrativo.

    Si se envía una solicitud POST con un formulario válido, se crea un nuevo usuario con los datos especificados.
    Si la solicitud es GET, se presenta un formulario vacío para ingresar datos.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP, que puede ser GET o POST.

    Returns
    -------
    JsonResponse
        Si la solicitud es POST y válida, retorna un JSON con estado de éxito.

    HttpResponse
        Si la solicitud es GET o el formulario no es válido, renderiza el formulario HTML en `admin/usercreate.html`.

    See Also
    --------
    UserCreationForm : Formulario para capturar los datos del nuevo usuario.
    User : Modelo de usuario que se registra.
    Empresa : Modelo relacionado a la empresa a la que puede estar asignado el usuario.
    Role : Modelo que define los permisos del usuario.

    Notes
    -----
    - El formulario incluye campos como nombre, correo, empresa, rol, y permisos especiales (staff, superuser).
    - Si el formulario no es válido, los errores se imprimen en consola para depuración.
    - Se usa el método `create_user` que aplica hashing a la contraseña automáticamente.
    """
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Procesar el formulario y crear el usuario
            
            cleaned_data = form.cleaned_data
            indicador_ids = request.POST.getlist('company') #Captura múltiples valores
            
            #concepto.indicador.add(*indicadores)
            
            id_empresa = Empresa.objects.filter(idempresa__in=indicador_ids) if cleaned_data['company'] else None
            rol = Role.objects.get(id=cleaned_data['permission'])
            
            user = User.objects.create_user(
                first_name=cleaned_data['first_name'],
                last_name=cleaned_data['last_name'],
                email=cleaned_data['email'],
                password=cleaned_data['password1'],
                tipo_user=cleaned_data['role'],
                rol=rol,
                is_staff=cleaned_data['is_staff'],
                is_superuser=cleaned_data['is_superuser'],
                is_active=cleaned_data['is_active'],
            )
            
            if id_empresa != None :
                user.id_empresa.add(*id_empresa)
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Concepto guardado exitosamente'    
            response['X-Up-Location'] = reverse('admin:user')           
            return response
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
    else:
        form = UserCreationForm()
    return render(request, './admin/partials/usercreate.html', {'form': form})



def usercreate_edit(request,id):
    icon = 'success' 
    message = '¡Todo un éxito! El usuario fue actualizado,' 
    
    user = get_object_or_404(User, pk=id)
    
    data = {
        'email':user.email ,
        'first_name':user.first_name ,
        'last_name':user.last_name ,
        'role':user.tipo_user,
        'permission':user.rol.id ,
        'company' :[i.idempresa for i in user.id_empresa.all()],
        
        }
    

    form = UserEditForm(initial = data,id = id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST,id = id)
        if form.is_valid():
            
            email = form.cleaned_data['email']
            last_name = form.cleaned_data['last_name']
            first_name = form.cleaned_data['first_name']
            company = form.cleaned_data['company']            # Obtener el objeto grupo_dian
            role = form.cleaned_data['role']
            permission = form.cleaned_data['permission']
            

            if last_name != user.last_name:
                user.last_name = last_name
                
            if first_name != user.first_name:
                user.first_name = first_name
            
            if role != user.tipo_user:
                user.tipo_user = role
                
            if permission!= user.rol.id:
                user.rol = Role.objects.get(id= permission)
            
            
            
            if form.cleaned_data['new_pass'] : 
                passwordoriginal = generate_random_password()
                user.password = make_password(passwordoriginal)
                message += ' la contraseña cambiada sin dramas  ' 
                
                email_type = 'loginweb'
                context = {
                    'usuario': user.email,
                    'contrasena': passwordoriginal,
                }
                subject = '¡Contraseña renovada en Nomiweb! Como cambiar de look... pero más seguro'
                recipient_list = [user.email]
                
                if send_template_email(email_type, context, subject, recipient_list):
                    message += 'y el correo voló directo a su bandeja. ¡Como magia… pero con teclas!' 
                else:
                    message = '¡Uy! El correo electrónico tropezó en el camino y no llegó a su destino.' 
                    icon = 'error' 'success' 
            
            user.save() 
            user.id_empresa.set(company)
            
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = icon # URL para recargar la página principal   
            response['X-Up-message'] = urllib.parse.quote(message)    
            response['X-Up-Location'] = reverse('admin:user')           
            return response      
            
    return render(request, './admin/partials/editUserModal.html', {'form': form})