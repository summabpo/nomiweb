"""
Funciones de Formato de Valores

Estas funciones proporcionan métodos para formatear valores numéricos (enteros, flotantes) en cadenas de texto con separadores de miles y decimales, así como para manejar valores nulos o cero.

1. `format_value(value)`
    Formatea un valor entero a una cadena de texto con separadores de miles.

    Parámetros
    ----------
    value : int, float, str, None
        El valor a formatear. Puede ser un número entero, un flotante, una cadena de texto o None.

    Retorna
    -------
    str
        El valor formateado como una cadena de texto con separadores de miles (usando puntos como separadores).
        Si el valor es None, retorna '0'.

    Descripción
    -----------
    Esta función toma un valor numérico (puede ser entero o flotante) y lo convierte en una cadena de texto con el formato de miles, reemplazando las comas por puntos.
    Si el valor no es un número válido, la función lo retorna tal cual como una cadena de texto.

    Ejemplo
    -------
    format_value(1234567) -> '1.234.567'
    format_value('abc') -> 'abc'


2. `format_value_float(value)`
    Formatea un valor flotante a una cadena de texto con separadores de miles.

    Parámetros
    ----------
    value : float, int, str, None
        El valor a formatear. Puede ser un número flotante, un entero, una cadena de texto o None.

    Retorna
    -------
    str
        El valor formateado como una cadena de texto con separadores de miles (usando puntos como separadores).
        Si el valor es None, retorna '0'.

    Descripción
    -----------
    Esta función toma un valor flotante y lo convierte en una cadena de texto con el formato de miles, reemplazando las comas por puntos.
    Si el valor no es un número válido, la función lo retorna tal cual como una cadena de texto.

    Ejemplo
    -------
    format_value_float(1234567.89) -> '1.234.567.89'
    format_value_float('abc') -> 'abc'


3. `format_decimal(value)`
    Formatea un valor decimal a una cadena de texto con dos decimales y separadores de miles.

    Parámetros
    ----------
    value : float, int, str, None
        El valor a formatear. Puede ser un número decimal (flotante), un entero, una cadena de texto o None.

    Retorna
    -------
    str
        El valor formateado como una cadena de texto con dos decimales y separadores de miles (usando puntos como separadores).
        Si el valor es None, retorna '0.00'.

    Descripción
    -----------
    Esta función toma un valor numérico y lo convierte en una cadena de texto con el formato de miles y dos decimales, reemplazando las comas por puntos.
    Si el valor no es un número válido, la función lo retorna tal cual como una cadena de texto.

    Ejemplo
    -------
    format_decimal(1234567.891) -> '1.234.567,89'
    format_decimal('abc') -> 'abc'


4. `format_value_void(value)`
    Formatea un valor a una cadena de texto con separadores de miles, pero retorna un espacio vacío si el valor es None o 0.

    Parámetros
    ----------
    value : int, float, str, None
        El valor a formatear. Puede ser un número entero, un flotante, una cadena de texto, 0 o None.

    Retorna
    -------
    str
        El valor formateado como una cadena de texto con separadores de miles, o un espacio vacío si el valor es None o 0.
        Si el valor no es un número válido, lo retorna tal cual como una cadena de texto.

    Descripción
    -----------
    Esta función toma un valor numérico (puede ser entero o flotante) y lo convierte en una cadena de texto con el formato de miles, reemplazando las comas por puntos.
    Si el valor es None o 0, retorna un espacio vacío (' ').
    Si el valor no es un número válido, la función lo retorna tal cual como una cadena de texto.

    Ejemplo
    -------
    format_value_void(1234567) -> '1.234.567'
    format_value_void(0) -> ' '
    format_value_void('abc') -> 'abc'
"""




def format_value(value):
    if value is None:
        return '0'
    try:
        return "{:,}".format(int(value)).replace(",", ".")
    except ValueError:
        return str(value)
    
def format_value_float(value):
    if value is None:
        return '0'
    try:
        return "{:,}".format(float(value)).replace(",", ".")
    except ValueError:
        return str(value)

def format_decimal(value):
    if value is None:
        return '0.00'
    try:
        return "{:,.2f}".format(float(value)).replace(",", ".")
    except ValueError:
        return str(value)

def format_value_void(value):
    if value is None or value is 0:
        return ' '
    try:
        return "{:,}".format(int(value)).replace(",", ".")
    except ValueError:
        return str(value)
