

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
    
    # Retornar el nombre de la nómina con el formato requerido
    return f"Nomina {tiponomina} - {mes} - {ano}"