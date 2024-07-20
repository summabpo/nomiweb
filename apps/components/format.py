



def formttex(cadena, max_caracteres):
    # Verificar si la cadena excede el máximo de caracteres permitidos
    if len(cadena) > max_caracteres:
        raise ValueError(f'Cadena "{cadena}" excede el máximo de {max_caracteres} caracteres.')

    # Limitar la cadena al máximo de caracteres especificado
    cadena_limitada = cadena[:max_caracteres]

    # Rellenar con ceros a la izquierda si es necesario
    if len(cadena_limitada) < max_caracteres:
        cadena_formateada = cadena_limitada.zfill(max_caracteres)
    else:
        cadena_formateada = cadena_limitada

    return cadena_formateada


def formtnun(cadena, max_caracteres):
    if isinstance(cadena, (int, float)):
        cadena = f"{cadena:.2f}"
        
        
        if len(cadena) > max_caracteres:
            raise ValueError(f'Cadena "{cadena}" excede el máximo de {max_caracteres} caracteres.')
        # Verificar si la cadena excede el máximo de caracteres permitidos
        
    
        # Rellenar con ceros a la izquierda si es necesario
        if len(cadena) < max_caracteres:
            
            cadena = cadena.replace('.', '')
            cadena_formateada = cadena.zfill(max_caracteres)
        else:
            cadena_formateada = cadena

    return cadena_formateada
