from django.contrib.auth.backends import ModelBackend
from apps.common.models import User
from django.contrib.auth.hashers import check_password

"""
Backend de autenticación personalizado para el sistema de autenticación de Django.

Este backend de autenticación personalizado permite la autenticación de usuarios utilizando un modelo `User` 
personalizado. Se sobrecargan los métodos de autenticación y recuperación de usuario para verificar las credenciales 
de acceso y permitir o denegar el inicio de sesión.

Methods
-------
authenticate(request, username=None, password=None, **kwargs)
    Intenta autenticar al usuario proporcionando su nombre de usuario y contraseña. Si las credenciales son correctas,
    devuelve el objeto `User`; de lo contrario, retorna `None`.

get_user(user_id)
    Recupera el usuario a partir de su identificador (ID). Si no se encuentra al usuario, retorna `None`.

user_can_authenticate(username)
    Verifica si el usuario con el nombre de usuario proporcionado está activo. Retorna un valor booleano.

Parameters
----------
request : HttpRequest
    Objeto de solicitud HTTP que contiene los datos necesarios para el proceso de autenticación.
username : str
    El nombre de usuario del usuario que intenta iniciar sesión.
password : str
    La contraseña del usuario que intenta iniciar sesión.

Returns
-------
User or None
    Si las credenciales son correctas, retorna el objeto `User`. Si no, retorna `None`.

Notes
-----
Este backend utiliza el modelo `User` y la base de datos por defecto (`default`) para la autenticación.
La contraseña del usuario se valida utilizando el método `check_password` de Django.
"""


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.using("default").get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.using("default").get(pk=user_id)
        except User.DoesNotExist:
            return None

    def user_can_authenticate(self, username):
        user = User.objects.using("default").get(username=username)
        return user.is_active
