from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .custom_auth_backend import CustomAuthBackend 
from apps.login.middlewares import NombreDBSingleton

from django.contrib.sessions.backends.base import SessionBase


def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not TempSession().is_logged_in():
            return redirect('login:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def custom_permission(permission):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if TempSession().have_permission() != permission:
                return redirect('login:permission')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


class TempSession:
    """
    Una clase singleton que representa una sesión temporal.

    Esta clase proporciona funcionalidad para gestionar una sesión temporal con el propósito de autenticación de usuarios.
    Mantiene el estado de si un usuario ha iniciado sesión o no, así como los permisos y el tipo de usuario.

    Atributos:
        _instance (TempSession): La instancia singleton de la clase TempSession.
        user_logged_in (bool): Bandera que indica si un usuario ha iniciado sesión.
        permissions (list): Lista de permisos del usuario.
        user_type (str): Tipo de usuario (por ejemplo, 'admin', 'usuario_normal', etc.).
    """

    _instance = None
    user_logged_in = False
    permissions = []
    user_type = ""

    def __new__(cls, *args, **kwargs):
        """
        Sobrescribe el método __new__ para asegurar que solo se cree una instancia de TempSession.

        Args:
            *args: Argumentos posicionales adicionales.
            **kwargs: Argumentos clave adicionales.

        Returns:
            TempSession: La instancia singleton de la clase TempSession.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def login(self):
        """
        Inicia sesión de un usuario estableciendo la bandera user_logged_in en True.
        """
        self.user_logged_in = True

    def logout(self):
        """
        Cierra sesión de un usuario estableciendo la bandera user_logged_in en False y borrando los permisos y el tipo de usuario.
        """
        self.user_logged_in = False
        self.user_type = ""
        self.permissions = []

    def is_logged_in(self):
        """
        Verifica si un usuario ha iniciado sesión.

        Returns:
            bool: True si un usuario ha iniciado sesión, False en caso contrario.
        """
        return self.user_logged_in

    def set_user_type(self, user_type):
        """
        Establece el tipo de usuario.

        Args:
            user_type (str): Tipo de usuario.
        """
        self.user_type = user_type
        
    def have_permission(self):
        """
        Verifica si un usuario tiene permisos de accesso basado en su tipo de usuario  .

        Returns:
            regresa el tipo de usuario para validarlo con el tipo de usuarip que requiera la pagina 
        """
        return self.user_type


    def set_permissions(self, permissions):
        """
        Establece los permisos del usuario.

        Args:
            permissions (list): Lista de permisos del usuario.
        """
        self.permissions = permissions
