from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login , logout
from django.contrib import messages
from .forms import LoginForm
from .models import Usuario,Empresa

from apps.components.role_redirect  import redirect_by_role

from apps.login.middlewares import NombreDBSingleton




def login_view(request):
    request.session.clear()
    if request.user.is_authenticated:
        print(request.session)
    else:
        print('lleno')
        
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
                
                # singleton = NombreDBSingleton()
                # singleton.set_nombre_db(usuario.company.db_name)
                return redirect_by_role(usuario.role)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, './users/login.html', {'form': form})


def logout_view(request):
    singleton = NombreDBSingleton()
    singleton.set_nombre_db('default')
    request.session.clear()
    logout(request)
    
    return redirect('login:login')


def redirect_user(request):
    return redirect('login')





def prueba(request):
    usuario_data = request.session.get('usuario', {})
    
    print(request.session.items())
    rol = usuario_data.get('rol', None)
    compania = usuario_data.get('compania', None)
    
    return render(request, './users/prueba.html',{'compania':compania})

