from django.utils import timezone
from apps.common.models import EditHistory


def register_history(instance, user, changed_fields: dict, operation='update'):
    """
    instance → objeto del modelo (Empresa)
    user → request.user
    changed_fields → diccionario {campo: (valor_antiguo, valor_nuevo)}
    """

    for field, values in changed_fields.items():

        old_value, new_value = values

        # Solo registrar si realmente cambió
        if str(old_value) != str(new_value):

            EditHistory.objects.create(
                modified_model=instance.__class__.__name__,
                modified_object_id=instance.pk,
                user=user,
                modification_time=timezone.now(),
                operation_type=operation,
                field_name=field,
                old_value=old_value,
                new_value=new_value,
                description=f"Se modificó el campo {field}",
                id_empresa=instance
            )