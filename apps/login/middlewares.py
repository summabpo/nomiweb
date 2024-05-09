from django.utils.deprecation import MiddlewareMixin
from .models import Usuario
from django.urls import reverse

class DatabaseRouterMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            singleton = NombreDBSingleton()
            if request.user.is_authenticated:
                if 'usuario' in request.session and 'db' in request.session['usuario'] and not request.path == reverse('login:logout') and not request.path == reverse('login:login'):
                    print("estoy aqui 2 ")
                    db_name = request.session['usuario']['db']
                    singleton.set_nombre_db(db_name)
            else:
                singleton.set_nombre_db('default')
            
        except Exception as e:
            if  (request.path == reverse('login:login')  or request.path == reverse('login:logout') or request.path.startswith('/admin/') ) and request.method == 'POST':
                singleton.set_nombre_db('default')
                
class NombreDBSingleton:
    _instance = None
    nombre_db = 'default'

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def set_nombre_db(self, nombre_db):
        self.nombre_db = nombre_db

    def get_nombre_db(self):
        return self.nombre_db

    @classmethod
    def set_default(cls):
        cls.nombre_db = "default"
