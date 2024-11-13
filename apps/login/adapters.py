# users/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from apps.common.models import User
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from allauth.core.exceptions import ImmediateHttpResponse

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Verifica si el correo electrónico del usuario ya está registrado en la base de datos de usuarios de Django.
        Si el correo está registrado, conecta la cuenta social con el usuario correspondiente.
        Si el correo no está registrado, no se realiza ninguna acción y se redirige al login.
        """
        email = sociallogin.user.email  # Obtiene el correo del usuario que intenta hacer el login social
        
        try:
            # Verifica si el correo electrónico ya está registrado en la tabla User de Django
            user = User.objects.get(email=email)
            
            # Si el usuario ya existe y no está vinculado con el proveedor de cuenta social, lo conectamos
            if not SocialAccount.objects.filter(user=user, provider=sociallogin.account.provider).exists():
                sociallogin.user = user  # Asignamos el usuario al login social
                sociallogin.connect(request, user=user)  # Conectamos la cuenta social con el usuario

        except User.DoesNotExist:
            # Si el usuario no existe, redirigimos al login con un mensaje de error
            messages.error(request, "¡Ups! El usuario no existe. ¿Quizás fuiste registrado con otro correo?")
            # Redirige inmediatamente al login utilizando reverse para obtener la URL correcta
            raise ImmediateHttpResponse(redirect(reverse('login:login')))  

        except Exception as e:
            # En caso de cualquier otro error, mostramos un mensaje de error y redirigimos al login
            messages.error(request, f"¡Vaya! Algo salió mal... ¿Quizás un dragón saboteó el sistema? {str(e)}")
            # Redirige inmediatamente al login utilizando reverse para obtener la URL correcta
            raise ImmediateHttpResponse(redirect(reverse('login:login')))
