
from apps.common.models import Crearnomina 

MES_CHOICES = [
    ('', '--------------'),
    ('ENERO', 'Enero'),
    ('FEBRERO', 'Febrero'),
    ('MARZO', 'Marzo'),
    ('ABRIL', 'Abril'),
    ('MAYO', 'Mayo'),
    ('JUNIO', 'Junio'),
    ('JULIO', 'Julio'),
    ('AGOSTO', 'Agosto'),
    ('SEPTIEMBRE', 'Septiembre'),
    ('OCTUBRE', 'Octubre'),
    ('NOVIEMBRE', 'Noviembre'),
    ('DICIEMBRE', 'Diciembre')
]


def generar_nombre_nomina(name , idempresa):
    
    if "Quincenal" in name:
        if Crearnomina.objects.filter(nombrenomina=name, id_empresa=idempresa).exists():
            mensaje = f"{name} - #2"
        else:
            mensaje = f"{name} - #1"
    else:
        mensaje = f"{name}"
    return mensaje