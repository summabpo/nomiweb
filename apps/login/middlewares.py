from django.utils.deprecation import MiddlewareMixin
from .models import Usuario
from django.urls import reverse
from django.apps import apps
from django.db import connection
from .models import Usuario

class DatabaseRouterMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            singleton = NombreDBSingleton()
            if request.user.is_authenticated:
                if 'usuario' in request.session and 'db' in request.session['usuario'] and not request.path == reverse('login:logout') and not request.path == reverse('login:login'):
                    db_name = request.session['usuario']['db']
                    if self.db_has_table(db_name):
                        singleton.set_nombre_db(db_name)
                        print('1')
        except Exception as e:
            if  (request.path == reverse('login:login')  or request.path == reverse('login:logout') or request.path.startswith('/admin/') ) and request.method == 'POST':
                singleton.set_nombre_db('default')
                print('5')
            # Handle exception here

    def db_has_table(self, db_name):
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO '{}', public;".format(db_name))
            for model in connection.introspection.table_names(cursor):
                if self.table_exists_in_db(db_name, model):
                    return True
            return False

    def table_exists_in_db(self, db_name, table_name):
        with connection.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s)", [table_name])
            return cursor.fetchone()[0]
                
                
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
