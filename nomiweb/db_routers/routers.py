from django.db import connections, OperationalError
from apps.login.middlewares import NombreDBSingleton
from functools import lru_cache

class DatabaseRouter:
    def __init__(self):
        self.nombre_db_singleton = NombreDBSingleton()

    @lru_cache(maxsize=None)
    def table_exists(self, table_name, db_alias='default'):
        """
        Verifica si una tabla existe en la base de datos especificada.
        """
        try:
            with connections[db_alias].cursor() as cursor:
                cursor.execute("SELECT * FROM information_schema.tables WHERE table_name = %s", [table_name])
                return bool(cursor.fetchone())
        except OperationalError:
            return False

    def _determine_db(self, model):
        """
        Determina el nombre de la base de datos a utilizar para una operación.
        """
        nombre_db = self.nombre_db_singleton.get_nombre_db()
        if self.table_exists(model._meta.db_table):
            return 'default'
        else:
            return nombre_db

    def db_for_read(self, model, **hints):
        """
        Devuelve el nombre de la base de datos a utilizar para operaciones de lectura.
        """
        return self._determine_db(model)

    def db_for_write(self, model, **hints):
        """
        Devuelve el nombre de la base de datos a utilizar para operaciones de escritura.
        """
        return self._determine_db(model)

    def allow_relation(self, obj1, obj2, **hints):
        """
        Determina si la relación entre dos objetos debe ser permitida.
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Determina si las migraciones deben ser aplicadas en una base de datos particular.
        """
        return True
