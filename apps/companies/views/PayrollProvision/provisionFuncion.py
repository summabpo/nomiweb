def calcular_descuento(salario_persona, salario_minimo):
    # Definir los rangos y porcentajes
    rangos = [
        (4, 16, 1.0),   # De 4 a 16 veces el salario mínimo: 1.0%
        (16, 17, 1.2),  # De 16 a 17 veces el salario mínimo: 1.2%
        (17, 18, 1.4),  # De 17 a 18 veces el salario mínimo: 1.4%
        (18, 19, 1.6),  # De 18 a 19 veces el salario mínimo: 1.6%
        (19, 20, 1.8),  # De 19 a 20 veces el salario mínimo: 1.8%
        (20, float('inf'), 2.0)  # Más de 20 veces el salario mínimo: 2.0%
    ]
    
    # Verificar si el salario de la persona está dentro del rango válido
    if salario_persona < salario_minimo * 4:
        return 0

    # Encontrar el porcentaje aplicable basado en el salario
    for rango in rangos:
        rango_min, rango_max, porcentaje = rango
        limite_inferior = salario_minimo * rango_min
        limite_superior = salario_minimo * rango_max

        if limite_inferior <= salario_persona < limite_superior:
            # Calcular el monto a descontar
            monto_descuento = (porcentaje / 100) * salario_persona
            return monto_descuento

    # Si el salario supera el último rango
    if salario_persona >= salario_minimo * 20:
        return (2.0 / 100) * salario_persona

    return 0


def mes_a_numero(mes_texto):
    meses = {
        'enero': '01',
        'febrero': '02',
        'marzo': '03',
        'abril': '04',
        'mayo': '05',
        'junio': '06',
        'julio': '07',
        'agosto': '08',
        'septiembre': '09',
        'octubre': '10',
        'noviembre': '11',
        'diciembre': '12'
    }
    
    mes_texto = mes_texto.lower()  # Asegura que el texto esté en minúsculas
    return meses.get(mes_texto, 'Mes no válido')