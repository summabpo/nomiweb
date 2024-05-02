# middlewares.py
from django.utils.deprecation import MiddlewareMixin
from .models import Usuario,Empresa

class AddDBNameToRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            usuario = Usuario.filter_by_username(request.user.username)
            request.session['usuario'] = {
                        'rol': usuario.role,
                        'compania': usuario.company.name,
                        'db':usuario.company.db_name
                    }
            