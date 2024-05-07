from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .custom_auth_backend import CustomAuthBackend 
from apps.login.middlewares import NombreDBSingleton


def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        #backend = CustomAuthBackend()  
        if user:
            print('´prueba')
            return view_func(request, *args, **kwargs)
        else:
            print("El usuario está vacío. Redireccionando al inicio de sesión.")
            return redirect('login:login')
    return wrapper
