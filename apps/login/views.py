from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login , logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib import messages
from .forms import LoginForm ,PasswordResetForm , PasswordResetTokenForm
from django.conf import settings

from django.utils import timezone
import secrets
from apps.components.role_redirect  import redirect_by_role , redirect_by_role2
from apps.components.decorators import TempSession,custom_login_required , default_login
from apps.components.mail import send_template_email
from django.urls import reverse
from apps.common.models import User , Token
from django.contrib.auth import get_user_model


def Login_view(request):
    
    """
    Maneja la autenticación de usuarios en el sistema.

    Si el usuario ya está autenticado, redirige al dashboard o home correspondiente
    según su rol. Si no está autenticado, permite ingresar credenciales y 
    autenticar al usuario mediante correo electrónico y contraseña. En caso 
    de éxito, guarda datos relevantes del usuario en la sesión y redirige 
    según su rol.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP, que puede contener datos POST con las credenciales 
        de inicio de sesión del usuario.

    Returns
    -------
    HttpResponseRedirect
        Redirección al dashboard o home correspondiente si el usuario está autenticado o 
        si se autentica correctamente tras enviar el formulario.

    HttpResponse
        Respuesta que renderiza la plantilla de login con el formulario en caso 
        de acceso inicial o fallo de autenticación.

    See Also
    --------
    LoginForm : Formulario de autenticación con campos de correo y contraseña.
    redirect_by_role : Función que redirige al usuario autenticado según su rol.
    authenticate : Función de Django para autenticar credenciales de usuario.
    login : Función de Django para establecer la sesión del usuario autenticado.

    Notes
    -----
    Los datos del usuario autenticado se guardan en la sesión bajo la clave 
    `'usuario'` y contienen:
        - id : int
            Identificador del usuario.
        - rol : str
            Tipo de usuario (rol).
        - name : str
            Nombre completo del usuario.
        - idempleado : int or None
            Identificador del empleado relacionado (si aplica).
        - idempresa : int or None
            Identificador de la empresa relacionada (si aplica).

    El formulario renderizado en la plantilla `'./users/login.html'` permite 
    al usuario ingresar correo y contraseña para autenticarse.

    """
    if request.user.is_authenticated:
        rol = request.session.get('usuario', {}).get('rol')
        return redirect_by_role(rol)
    else:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                
                user = authenticate(request, email=email, password=password)
                
                if user is not None:
                    login(request, user)
                    complements = {
                        'id': user.id,
                        'rol': user.tipo_user,
                        'name': f"{user.first_name} {user.last_name}",
                        'idempleado': user.id_empleado.idempleado if user.id_empleado else None ,
                        'idempresa': user.id_empresa.first().idempresa if user.id_empresa.count() == 1 else None,
                        'nombre_empresa': user.id_empresa.first().nombreempresa if user.id_empresa.count() == 1 else None
                    }
                    
                    request.session['usuario'] = complements
                    return redirect_by_role(user.tipo_user)
                else:
                    messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            form = LoginForm()
        return render(request, './users/login.html', {'form': form})





def login_home(request, sociallogin=None, **kwargs):
    """
    Vista intermedia para completar el inicio de sesión tras autenticación social (OAuth).

    Esta vista se utiliza como puente después de que django-allauth completa un proceso 
    de autenticación social exitoso . Recupera los datos del usuario 
    autenticado desde la sesión (`_auth_user_id` y `_auth_user_backend`), inicia sesión 
    en Django utilizando esos valores, y almacena información adicional del usuario 
    en la sesión interna bajo la clave `'usuario'`. Finalmente, redirige según el rol del usuario.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP con los datos de sesión generados por django-allauth.

    sociallogin : allauth.account.models.SocialLogin, optional
        Objeto opcional que representa la autenticación social realizada. Aunque no se usa directamente
        en esta vista, puede ser útil si se extiende la funcionalidad.

    **kwargs : dict
        Parámetros adicionales que pueden ser pasados desde el flujo de autenticación de allauth.

    Returns
    -------
    HttpResponseRedirect
        Redirección al dashboard o home correspondiente, dependiendo del rol del usuario autenticado.

    See Also
    --------
    login : Función de Django que inicia sesión para un usuario autenticado.
    get_user_model : Devuelve el modelo de usuario activo.
    redirect_by_role : Función personalizada que determina la vista a la que se debe redirigir al usuario.

    Notes
    -----
    Esta función asume que django-allauth ya ha autenticado al usuario correctamente 
    y ha almacenado en la sesión los campos:
        - '_auth_user_id' : str
            ID del usuario autenticado.
        - '_auth_user_backend' : str
            Ruta del backend utilizado para autenticar al usuario.

    La función carga el modelo de usuario, verifica su existencia, ejecuta el login
    y guarda los siguientes datos adicionales en la sesión:
        - rol : str
            Tipo de usuario.
        - name : str
            Nombre completo.
        - idempleado : int or None
            ID del empleado asociado (si aplica).
        - idempresa : int or None
            ID de la empresa asociada (si aplica).

    """
    user_id = request.session.get('_auth_user_id')
    backend = request.session.get('_auth_user_backend')
    if user_id and backend:
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        # Si el usuario está autenticado, puedes iniciar sesión
        if user:
            login(request, user, backend=backend)
            
            rol = user.tipo_user 
            request.session['usuario'] = {
                'id': user.id,
                'rol': user.tipo_user,
                'name': f"{user.first_name} {user.last_name}",
                'idempleado': user.id_empleado.idempleado if user.id_empleado else None,
                'idempresa': user.id_empresa.first().idempresa if user.id_empresa.count() == 1 else None,
                'nombre_empresa': user.id_empresa.first().nombreempresa if user.id_empresa.count() == 1 else None
            }
    return redirect_by_role(rol)

@login_required
def logout_view(request):
    """
    Cierra la sesión del usuario y realiza tareas de limpieza adicionales.

    Esta vista requiere que el usuario esté autenticado. Cuando se accede,
    se termina la sesión activa de Django y se ejecuta un método adicional 
    `logout()` desde una instancia de `TempSession`, que puede encargarse 
    de tareas personalizadas como limpieza de cache, cierre de sesiones paralelas,
    auditoría, etc. Finalmente, redirige al usuario a la vista de login.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP del usuario que desea cerrar sesión.

    Returns
    -------
    HttpResponseRedirect
        Redirección a la vista de inicio de sesión definida por el namespace 'login:login'.

    See Also
    --------
    logout : Función de Django que elimina la sesión del usuario autenticado.
    TempSession.logout : Método personalizado que realiza tareas adicionales al cerrar sesión.

    Notes
    -----
    Esta vista utiliza el decorador `@login_required`, por lo tanto, solo está accesible
    para usuarios que ya han iniciado sesión.

    La clase `TempSession` debe estar definida en la carpeta de components - archivo de decoradores  y su método `logout()`
    puede incluir lógica adicional como eliminar datos temporales, revocar tokens, o registrar el cierre.

    
    """
    logout(request)
    session = TempSession()
    session.logout()
    return redirect('login:login')




def password_reset_view(request):
    """
    Vista para manejar la solicitud de restablecimiento de contraseña mediante un enlace con token temporal.

    Permite que un usuario solicite el restablecimiento de su contraseña proporcionando su correo electrónico.
    Si el correo está registrado en el sistema, se genera un token temporal que se asocia al usuario en la base de datos
    y se envía un correo electrónico con un enlace único para restablecer la contraseña.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los datos del formulario de restablecimiento de contraseña
        (si el método es POST) o muestra el formulario vacío (si el método es GET).

    Returns
    -------
    HttpResponse
        Si la solicitud es exitosa, se redirige a la página de login con un mensaje de éxito.
        En caso de error, se renderiza nuevamente el formulario con mensajes de error.

    See Also
    --------
    PasswordResetForm : Formulario utilizado para validar el correo electrónico del usuario.
    Token : Modelo que almacena el token temporal para el restablecimiento de contraseña.
    send_template_email : Función utilizada para enviar un correo electrónico con el enlace de restablecimiento.

    Notes
    -----
    - El token temporal es generado utilizando `secrets.token_urlsafe` para garantizar su seguridad.
    - El enlace de restablecimiento se genera concatenando la URL base del sitio (`settings.HOSTNAME`)
        con el token generado.
    - El token se almacena en la base de datos junto con un timestamp para rastrear su creación.
    - El sistema muestra un mensaje de error si el correo no está registrado en el sistema.

    """
    
    
    
    url1 = settings.HOSTNAME 
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                token_temporal = secrets.token_urlsafe(50)
                token = Token.objects.create(
                    user=user,
                    token_temporal=token_temporal,
                    tiempo_creacion=timezone.now()
                )
                
                email_type = 'token' 
                url =  url1 + 'password/reset/' + str(token_temporal) 
                context = {'url': url}  
                subject = 'Solicitud de restablecimiento de contraseña'  
                recipient_list = [ email ]
                
                
                if send_template_email(email_type, context, subject, recipient_list):
                    messages.success(request, 'El Correo ha sido Enviado Con éxito.')
                else:
                    messages.error(request, 'Hubo un error al enviar el correo. Por favor, intenta nuevamente más tarde.')
                    
                return redirect('login:login')             
            else:
                messages.error(request,'Parece que el correo ingresado no coincide con ningún usuario.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    print(error)
                    messages.error(request, f"Error en el campo : {error}")
            
    else:
        form = PasswordResetForm
    return render(request, 'users/password_reset_form.html', {'form': form})


def password_reset_token(request, token):
    """
    Vista para restablecer la contraseña de un usuario utilizando un token temporal.

    Esta vista valida el token temporal proporcionado en la URL. Si el token es válido y activo, se presenta un
    formulario para que el usuario ingrese una nueva contraseña. Al enviar el formulario con éxito, la contraseña
    del usuario se actualiza, el token se invalida y se redirige al usuario a la página de login.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los datos del formulario (si el método es POST) o muestra el formulario vacío
        (si el método es GET).

    token : str
        Token temporal recibido en la URL para validar el acceso al proceso de restablecimiento de contraseña.

    Returns
    -------
    HttpResponse
        Si el token es válido y el formulario es enviado correctamente, redirige al login con un mensaje de éxito.
        Si el token no es válido o está inactivo, muestra un error en la vista correspondiente.

    See Also
    --------
    Token : Modelo que almacena los tokens temporales de restablecimiento de contraseña.
    PasswordResetTokenForm : Formulario utilizado para validar la nueva contraseña del usuario.
    make_password : Función de Django que encripta la nueva contraseña antes de almacenarla.

    Notes
    -----
    - El token es buscado en la base de datos y se verifica si está activo. Si el token está marcado como `estado=False`,
        se considera inactivo y se muestra un error.
    - Si el token es válido, se muestra el formulario donde el usuario puede introducir y contraseña y su respectiva validacion de la contraseña.
    - Al enviar el formulario, la contraseña del usuario se actualiza utilizando `make_password` para encriptarla.
    - El token se invalida estableciendo `estado=False` para evitar que se utilice nuevamente.
    - Si el token no existe en la base de datos, se muestra una página de error.

    """
    # Verifica si el token existe
    if Token.objects.filter(token_temporal=token).exists():
        token = Token.objects.get(token_temporal=token)
        
        # Verifica si el token está en estado False
        if not token.estado:
            return render(request, 'users/errortoken.html')
        
        if request.method == 'POST':
            form = PasswordResetTokenForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data.get('password1')
                
                user = User.objects.get(email=token.user.email)
                user.password = make_password(password)
                user.save()
                token.estado = False
                token.save()
                
                messages.success(request, 'La contraseña ha sido actualizada con éxito')
                return redirect('login:login')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en el campo: {error}")
        else:
            form = PasswordResetTokenForm()
            
        return render(request, 'users/password_reset_token.html', {'form': form})
    else:
        return render(request, 'users/errortoken.html')

    
    







@custom_login_required
def require_permission(request):
    if request.method == 'POST':
        session = TempSession()
        return redirect_by_role(session.have_permission())
    return render(request, './users/permission.html')


def terms_and_conditions(request):
    return render(request, './users/terms_and_conditions.html')

def privacy_policy(request):
    return render(request, './users/privacy_policy.html')

#! errores 

def error_page(request):
    return render(request, './users/error_page.html')



def custom_400(request, exception):
    """
    Vista para manejar el error 400 (Bad Request).
    """
    return render(request, './error/400.html',{})

def custom_403(request, exception):
    """
    Vista para manejar el error 403 (Forbidden).
    """
    return render(request, './error/403.html',{})

def custom_404(request, exception):
    """
    Vista para manejar el error 404 (Página no encontrada).
    """
    return render(request, './error/404.html',{})


def custom_500(request):
    """
    Vista para manejar el error 500 (Internal Server Error).
    """
    return render(request, './error/500.html',{})