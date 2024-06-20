class DatabaseRouter:
    def db_for_read(self, model, **hints):
        """
        Retorna el nombre de la base de datos a utilizar para operaciones de lectura.
        """
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Retorna el nombre de la base de datos a utilizar para operaciones de escritura.
        """
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Determina si la relación entre dos objetos debe ser permitida.
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Determina si las migraciones deben ser aplicadas en una base de datos particular.
        """
        return db == 'default'
