from apps.login.middlewares import NombreDBSingleton

class DatabaseRouter:
    def db_for_read(self, model, **hints):
        # usuario_data = getattr(request,'session', {}).get('usuario', 'default') 
        # db = usuario_data.get('db', None)
    
        singleton = NombreDBSingleton()
        nombre_db = singleton.get_nombre_db()
        print(nombre_db)
        return nombre_db

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)
    
    
    
    
# class RouterAuth:
#     @staticmethod
#     def db_for_read(model, **hints):
#         return 'default'

#     @staticmethod
#     def db_for_write(model, **hints):
#         return 'default'

#     @staticmethod
#     def allow_relation(obj1, obj2, **hints):
#         if obj1._state.db == 'default' and obj2._state.db == 'default':
#             return True
#         return None

#     @staticmethod
#     def allow_migrate(db, app_label, model_name=None, **hints):
#         return db == 'default'

# class RouterLectaen:
#     @staticmethod
#     def db_for_read(model, **hints):
#         return 'lectaen'

#     @staticmethod
#     def db_for_write(model, **hints):
#         return 'lectaen'

#     @staticmethod
#     def allow_relation(obj1, obj2, **hints):
#         if obj1._state.db == 'lectaen' and obj2._state.db == 'lectaen':
#             return True
#         return None

#     @staticmethod
#     def allow_migrate(db, app_label, model_name=None, **hints):
#         return db == 'lectaen'
    
    
# class RouterLentes:
#     @staticmethod
#     def db_for_read(model, **hints):
#         return 'nwp_lentes'

#     @staticmethod
#     def db_for_write(model, **hints):
#         return 'nwp_lentes'

#     @staticmethod
#     def allow_relation(obj1, obj2, **hints):
#         if obj1._state.db == 'nwp_lentes' and obj2._state.db == 'nwp_lentes':
#             return True
#         return None

#     @staticmethod
#     def allow_migrate(db, app_label, model_name=None, **hints):
#         return db == 'nwp_lentes'

