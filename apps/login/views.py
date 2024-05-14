from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login , logout
from django.contrib import messages
from .forms import LoginForm , MiFormulario ,PasswordResetForm , PasswordResetTokenForm
from .models import Usuario,Empresa,Token
from django.utils import timezone
from django.contrib.auth.models import User
import secrets
from apps.components.role_redirect  import redirect_by_role
from apps.login.middlewares import NombreDBSingleton
from apps.components.decorators import TempSession,custom_login_required , default_login



@default_login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                
                login(request, user)
                usuario = Usuario.filter_by_username(request.user.username)
                request.session['usuario'] = {
                            'rol': usuario.role,
                            'compania': usuario.company.name,
                            'db':usuario.company.db_name
                        }
                session = TempSession()
                session.login()
                session.set_user_type(usuario.role)
                return redirect_by_role(usuario.role)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, './users/login.html', {'form': form})



@custom_login_required
def logout_view(request):
    singleton = NombreDBSingleton()
    singleton.set_nombre_db('default')
    request.session.clear()
    logout(request)
    session = TempSession()
    session.logout()
    return redirect('login:login')



def password_reset_view(request):
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
                messages.success(request, 'El Correo ha sido Enviado Con EXITO')
                print(token)
                
            else:
                messages.error(request,'Parece que el correo ingresado no coincide con ningún usuario.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo '{field}': {error}")
            
    else:
        form = PasswordResetForm
    return render(request, 'users/password_reset_form.html', {'form': form})


def password_reset_token(request,token):
    
    try:
        token = Token.objects.get(token_temporal=token)
        if request.method == 'POST':
            form = PasswordResetTokenForm(request.POST)
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
                    messages.success(request, 'El Correo ha sido Enviado Con EXITO')
                    print(token)
                    
                else:
                    messages.error(request,'Parece que el correo ingresado no coincide con ningún usuario.')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en el campo '{field}': {error}")
                
        else:
            form = PasswordResetTokenForm
            
        return render(request, 'users/password_reset_token.html', {'form': form})
    except :
    
        return render(request, 'users/errortoken.html')
    
    
    
    
    
    



@custom_login_required
def prueba(request):
    if request.method == 'POST':
        form = MiFormulario(request.POST)
        if form.is_valid():
            print(request.POST.get('opciones_1'))
            print(request.POST.get('opciones_2'))
            pass
    else:
        form = MiFormulario()
    
    return render(request, './users/prueba.html',{'form': form})


@custom_login_required
def require_permission(request):
    if request.method == 'POST':
        session = TempSession()
        return redirect_by_role(session.have_permission())
    return render(request, './users/permission.html')








#! errores 
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