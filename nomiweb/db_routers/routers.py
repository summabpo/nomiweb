from apps.login.middlewares import NombreDBSingleton

class DatabaseRouter:
    def db_for_read(self, model, **hints):
        singleton = NombreDBSingleton()
        nombre_db = singleton.get_nombre_db()
        return nombre_db

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        # Permitir relaciones si ambos objetos están en la misma base de datos
        if obj1._state.db == obj2._state.db:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Aquí puedes definir tus reglas de migración si es necesario
        return True
