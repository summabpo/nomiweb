class RouterAuth:
    @staticmethod
    def db_for_read(model, **hints):
        return 'default'

    @staticmethod
    def db_for_write(model, **hints):
        return 'default'

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        if obj1._state.db == 'default' and obj2._state.db == 'default':
            return True
        return None

    @staticmethod
    def allow_migrate(db, app_label, model_name=None, **hints):
        return db == 'default'

class RouterLectaen:
    @staticmethod
    def db_for_read(model, **hints):
        return 'lectaen'

    @staticmethod
    def db_for_write(model, **hints):
        return 'lectaen'

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        if obj1._state.db == 'lectaen' and obj2._state.db == 'lectaen':
            return True
        return None

    @staticmethod
    def allow_migrate(db, app_label, model_name=None, **hints):
        return db == 'lectaen'
