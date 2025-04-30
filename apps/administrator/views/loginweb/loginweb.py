from django.shortcuts import render, redirect
from django.contrib import messages
from apps.components.mail import send_template_email
from django.contrib.auth.hashers import make_password
from apps.common.models import Empresa , Role , Contratos, Contratosemp ,User
import random
import string

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

def create_user_and_usuario(email, pnombre, papellido, password, empresa, id_empleado):
    """
    Crea un nuevo usuario en el sistema a partir de los datos del empleado.

    Parameters
    ----------
    email : str
        Correo electrónico del nuevo usuario.
    pnombre : str
        Primer nombre del usuario.
    papellido : str
        Primer apellido del usuario.
    password : str
        Contraseña ya encriptada para el usuario.
    empresa : int
        ID de la empresa asociada.
    id_empleado : int
        ID del empleado asociado (referencia a Contratosemp).

    Returns
    -------
    tuple[bool, User or None]
        - `True` y el objeto `User` si la creación fue exitosa.
        - `False` y `None` si ocurrió un error.

    Notes
    -----
    - Se asigna automáticamente el `Role` con ID 1.
    - Si hay errores (por ejemplo, empresa o empleado no encontrados), se captura y retorna `False`.
    """
    
    try:
        empresa = Empresa.objects.get( idempresa = empresa )
        
        empleado = Contratosemp.objects.get(idempleado = id_empleado) 
        
        user = User.objects.create(
            first_name=pnombre,
            last_name=papellido,
            email=email,
            tipo_user = 'employee',
            id_empresa = empresa ,
            rol = Role.objects.get(id = 1),
            password=password,
            id_empleado = empleado,
            is_staff=False,
            is_superuser=False,
            is_active=True
        )
        user.save()
        print(user)
        return True, user
    except Exception as e:
        print(e)
        return False, None 



def loginweb_admin(request):
    """
    Crea usuarios automáticamente desde la lista de empleados activos con contrato, y les envía sus credenciales por correo.

    Si se envía un POST con IDs seleccionados, genera una contraseña aleatoria para cada uno, 
    crea o actualiza su usuario, y envía el acceso por correo.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP, puede ser GET o POST.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla `admin/loginweb.html` con la lista de empleados si es GET, o redirige con mensajes si es POST.

    Notes
    -----
    - En modo POST:
        - Verifica si el usuario ya existe. Si no, lo crea con rol fijo (ID=1).
        - Se encripta la nueva contraseña con `make_password`.
        - Se envía un correo usando `send_template_email` con tipo `'loginweb'`.
    - Los destinatarios están momentáneamente quemados para pruebas.
    - Muestra mensajes `success` o `error` dependiendo del resultado.
    """
    if request.method == 'POST':
        
        selected_ids = request.POST.getlist('selected_ids')
        
        if selected_ids:
            for selected in selected_ids:
                try:
                    usertempo = Contratosemp.objects.get(idempleado = int(selected))
                    usuario = User.objects.get(id_empleado = int(selected))
                    
                except Contratosemp.DoesNotExist:
                    messages.error(request, "No se encontró el empleado con ID seleccionado.")
                    return redirect('admin:loginweb')
                except User.DoesNotExist:
                    usuario = None
                passwordoriginal = generate_random_password()
                password = make_password(passwordoriginal)
                
                if usuario:
                    usuario.password = password
                    usuario.save()
                    
                else:
                    try:
                        empresa = Empresa.objects.get( idempresa = usertempo.id_empresa.idempresa )
                        success, user  = create_user_and_usuario(usertempo.email, usertempo.pnombre, usertempo.papellido, password, empresa.idempresa, usertempo.idempleado)
                        if not success:
                            messages.error(request,"Error al crear el usuario.")
                    except Empresa.DoesNotExist:
                        messages.error(request, "No se encontró la empresa.")
                        return redirect('admin:loginweb')
                    except Exception as e:
                        messages.error(request, f"Error al crear el usuario: {e}")
                        return redirect('admin:loginweb')

                email_type = 'loginweb'
                context = {
                    'nombre_usuario': usertempo.pnombre,
                    'usuario': usertempo.email,
                    'contrasena': passwordoriginal,
                }
                subject = '¡Bienvenido a Nomiweb! Tu nueva plataforma de nóminas... ¡y tu mejor amigo!'
                recipient_list = ['mikepruebas@yopmail.com','manuel.david.13.b@gmail.com']
                #recipient_list = [usertempo.email]

                if send_template_email(email_type, context, subject, recipient_list):
                    messages.success(request, 'Los usuarios han sido enviados correctamente.')
                else:
                    messages.error(request, 'Todo lo que podria salir mal, salio mal')
                    return redirect('admin:loginweb')
                
            messages.success(request, 'Los usuarios han sido enviados correctamente.')
            return redirect('admin:loginweb')
                
    empleados = []
    
    contratos_empleados = Contratos.objects\
    .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede')\
    .filter(estadocontrato=1)\
    .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
            'idempleado__snombre', 'cargo__nombrecargo', 'idempleado__idempleado',
            'tipocontrato__tipocontrato', 'idempleado__email','idempleado__id_empresa__nombreempresa')

    empleados = [
        {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': f"{contrato['idempleado__papellido']} {contrato['idempleado__pnombre']} {contrato['idempleado__snombre']}",
            'cargo': contrato['cargo__nombrecargo'],
            'tipocontrato': contrato['tipocontrato__tipocontrato'],
            'idempleado': contrato['idempleado__idempleado'],
            'email': contrato['idempleado__email'],
            'empresa': contrato['idempleado__id_empresa__nombreempresa'],
        }
        for contrato in contratos_empleados
    ]

        
    return render(request, './admin/loginweb.html', {'empleados':empleados })



def edit_main(request):
    """
    Edita el correo electrónico de un empleado y su usuario asociado.

    Permite actualizar el correo de un empleado (`Contratosemp`) y su correspondiente usuario (`User`) desde el panel administrativo.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP, debe ser POST con campos `correo1` y `correo2`.

    Returns
    -------
    HttpResponseRedirect
        Redirige a la vista `admin:loginweb` con mensajes de éxito o error.

    Notes
    -----
    - `correo2` es el correo original actual del empleado.
    - `correo1` es el nuevo correo que se desea establecer.
    - Se asegura que el nuevo correo no sea idéntico al anterior.
    - El cambio se realiza en ambas tablas: `Contratosemp` y `User`.
    """
    if request.method == 'POST':
        correo1 = request.POST.get('correo1')
        correo2 = request.POST.get('correo2')
        
        try:
            usertempo = Contratosemp.objects.get(email = correo2)
        except Contratosemp.DoesNotExist:
            messages.error(request, 'No se encontró empleado con el correo electrónico proporcionado.')
            return redirect('admin:loginweb')
        
        try:
            usuario = User.objects.get(email = correo2 )
        except User.DoesNotExist:
            messages.error(request, 'No se encontró un usuario con el Correo proporcionado. Por favor, asegúrese de que el usuario esté activo antes de intentar cambiar su correo electrónico.')
            return redirect('admin:loginweb')
        
        if correo1 == correo2:
            messages.warning(request, 'El correo electrónico ingresado ya está registrado para este empleado.')
            return redirect('admin:loginweb')
        else:
            usertempo.email = correo1
            try:
                usertempo.save( )
            except Exception as e:
                print(f"Error saving usertempo: {e}")
                messages.error(request, 'Error al actualizar el correo electrónico del empleado.')
                return redirect('admin:loginweb')
            
            usuario.email = correo1
            try:
                usuario.save()
                
            except Exception as e:
                print(f"Error saving usuario.user: {e}")
                messages.error(request, 'Error al actualizar el correo electrónico del empleado.')
                return redirect('admin:loginweb')
            
            messages.success(request, 'Correo electrónico actualizado correctamente.')
            return redirect('admin:loginweb')


        
    
    

