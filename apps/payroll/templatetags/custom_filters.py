from django import template

register = template.Library()

@register.filter
def format_currency(value):
    """
    Formatea un número como una cantidad de dinero con el formato adecuado para algunas monedas.
    value: valor a formatear
    currency: símbolo o código de la moneda (por defecto 'COP')
    """
    try:
        # Convierte el valor a float
        value = float(value)
        
        # Separamos la parte entera y la parte decimal
        integer_part, decimal_part = str(value).split(".")
        
        # Formateamos la parte entera con punto como separador de miles
        integer_part = integer_part[::-1]  # Revertir la cadena para poder agregar el punto
        integer_part = '.'.join([integer_part[i:i+3] for i in range(0, len(integer_part), 3)])[::-1]  # Agrupar cada 3 caracteres y revertir la cadena de nuevo
        
        # Limitar a 2 decimales en la parte decimal
        decimal_part = decimal_part[:2]
        
        # Unir la parte entera y decimal con coma como separador decimal
        formatted_value = f"{integer_part},{decimal_part}"
        
        return f"{formatted_value}"
    except (ValueError, TypeError):
        return value


@register.filter
def zip_lists(value, arg):
    return zip(value, arg)