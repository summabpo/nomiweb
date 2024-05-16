from django.db import connection, OperationalError
from apps.login.middlewares import NombreDBSingleton

class DatabaseRouter:
    def table_exists(self, table_name, db_alias):
        """
        Verifica si una tabla existe en la base de datos especificada.
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM information_schema.tables WHERE table_name = %s", [table_name])
                return bool(cursor.fetchone())
        except OperationalError:
            return False

    def db_for_read(self, model, **hints):
        """
        Devuelve el nombre de la base de datos a utilizar para operaciones de lectura.
        """
        
        nombre_db = NombreDBSingleton().get_nombre_db()
        if self.table_exists(model._meta.db_table, 'default'):
            return 'default'
        else:
            return nombre_db

    def db_for_write(self, model, **hints):
        """
        Devuelve el nombre de la base de datos a utilizar para operaciones de escritura.
        
        """
        nombre_db = NombreDBSingleton().get_nombre_db()
        if self.table_exists(model._meta.db_table, 'default'):
            return 'default'
        else:
            return nombre_db

    def allow_relation(self, obj1, obj2, **hints):
        """
        Determina si la relación entre dos objetos debe ser permitida.
        """
        # Permitir relaciones entre objetos sin importar la base de datos
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Determina si las migraciones deben ser aplicadas en una base de datos particular.
        """
        return True