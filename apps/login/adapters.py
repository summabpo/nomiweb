from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import login
from apps.components.role_redirect  import redirect_by_role 

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def post_social_login(self, request, sociallogin):
        user = sociallogin.user
        
        print('--------------')
        print(user)
        print('--------------')
        print('aqui andamos ')
        print('--------------')
        login(request, user)  # Iniciar sesión con el usuario autenticado
        
        # Extraer y almacenar el rol del usuario y otros detalles en la sesión
        rol = user.tipo_user
        request.session['usuario'] = {
            'rol': rol,
            'name': f"{user.first_name} {user.last_name}",
            'idempleado': user.id_empleado.idempleado if user.id_empleado else None,
            'idempresa': user.id_empresa.idempresa if user.id_empresa else None
        }
        
        # Redirigir según el rol
        return redirect_by_role(rol)