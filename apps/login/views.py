from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login , logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib import messages
from .forms import LoginForm , MiFormulario ,PasswordResetForm , PasswordResetTokenForm
from django.conf import settings

from django.utils import timezone
import secrets
from apps.components.role_redirect  import redirect_by_role , redirect_by_role2
from apps.components.decorators import TempSession,custom_login_required , default_login
from apps.components.mail import send_template_email
from django.urls import reverse
from apps.common.models import User , Token
from django.contrib.auth import get_user_model






# class Login_View(View):
#     def get(self, request):        
#         form = LoginForm()
#         return render(request, './users/login.html', {'form': form})

#     def post(self, request):
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             user = authenticate(request, email=email, password=password)
#             if user is not None:
#                 login(request, user)
#                 complements = {
#                     'rol': user.role,
#                     'name': f"{user.first_name} {user.last_name}",
#                     'id': user.id_empleado
#                 }
#                 request.session['usuario'] = complements
#                 return redirect_by_role(user.role)
#             else:
#                 messages.error(request, 'Usuario o contraseña incorrectos.')
#         return render(request, './users/login.html', {'form': form})

def Login_view(request):
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
                        'rol': user.tipo_user,
                        'name': f"{user.first_name} {user.last_name}",
                        'idempleado': user.id_empleado.idempleado if user.id_empleado else None ,
                        'idempresa': user.id_empresa.idempresa if user.id_empresa else None
                    }
                    request.session['usuario'] = complements
                    return redirect_by_role(user.tipo_user)
                else:
                    messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            form = LoginForm()
        return render(request, './users/login.html', {'form': form})




def login_home(request, sociallogin=None, **kwargs):
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
                'rol': rol,
                'name': f"{user.first_name} {user.last_name}",
                'idempleado': user.id_empleado.idempleado if user.id_empleado else None,
                'idempresa': user.id_empresa.idempresa if user.id_empresa else None
            }
    return redirect_by_role(rol)

@login_required
def logout_view(request):
    logout(request)
    session = TempSession()
    session.logout()
    return redirect('login:login')




def password_reset_view(request):
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
    # Verifica si el token existe
    if Token.objects.filter(token_temporal=token).exists():
        token = Token.objects.get(token_temporal=token)
        
        # Verifica si el token está en estado False
        if not token.estado:
            return render(request, 'users/errortoken.html')
        
        if request.method == 'POST':
            form = PasswordResetTokenForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
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
    return render(request, './users/prueba.html')



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