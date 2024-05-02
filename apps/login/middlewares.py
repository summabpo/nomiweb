from django.utils.deprecation import MiddlewareMixin
from .models import Usuario
from django.urls import reverse

class DatabaseRouterMiddleware(MiddlewareMixin):
    def process_request(self, request):
        singleton = NombreDBSingleton()
        # if  request.method == 'GET' and singleton.get_nombre_db() == "default" and not request.path == reverse('login:logout') and not request.path == reverse('login:login') :
        #     print("Middleware ejecutándose en una solicitud GET")
        #     singleton.set_nombre_db('lectaen')
        if  request.path == reverse('login:login')  and request.path == reverse('login:logout') and not request.method == 'GET':
            print("Middleware ejecutándose en una solicitud GET")
            singleton.set_nombre_db('default')
        else : 
            singleton.set_nombre_db('lectaen')
            
            
class NombreDBSingleton:
    _instance = None
    nombre_db = 'lectaen'

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
