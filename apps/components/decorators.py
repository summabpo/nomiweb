from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .custom_auth_backend import CustomAuthBackend 
from apps.login.middlewares import NombreDBSingleton


def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not TempSession().is_logged_in():
            return redirect('login:login')
        return view_func(request, *args, **kwargs)
    return wrapper


class TempSession:
    """
    Una clase singleton que representa una sesión temporal.

    Esta clase proporciona funcionalidad para gestionar una sesión temporal con el propósito de autenticación de usuarios.
    Mantiene el estado de si un usuario ha iniciado sesión o no.

    Atributos:
        _instance (TempSession): La instancia singleton de la clase TempSession.
        user_logged_in (bool): Bandera que indica si un usuario ha iniciado sesión.
    """

    _instance = None
    user_logged_in = False

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
        Cierra sesión de un usuario estableciendo la bandera user_logged_in en False.
        """
        self.user_logged_in = False

    def is_logged_in(self):
        """
        Verifica si un usuario ha iniciado sesión.

        Returns:
            bool: True si un usuario ha iniciado sesión, False en caso contrario.
        """
        return self.user_logged_in
