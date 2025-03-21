
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


def generar_nombre_nomina(tiponomina, fechainicial):
    # Obtener el mes en letras y en mayúsculas
    mes = MES_CHOICES[fechainicial.month][0] if fechainicial.month else ''
    # Obtener el año
    ano = fechainicial.year
    
    if tiponomina == 'Quincenal':
        mensaje = f"Nómina {tiponomina} - {mes} - {ano} - #1"
        if Crearnomina.objects.filter(nombrenomina=mensaje).exists():
            mensaje = f"Nómina {tiponomina} - {mes} - {ano} -  #2"
    else:
        mensaje = f"Nómina {tiponomina} - {mes} - {ano}"
    
    
    # Retornar el nombre de la nómina con el formato requerido
    return mensaje