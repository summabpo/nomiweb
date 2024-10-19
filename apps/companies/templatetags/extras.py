from django import template

register = template.Library()

@register.filter
def multiply(value1, value2):
    try:
        return int(float(value1) * float(value2))  # Multiplica y convierte a entero
    except (ValueError, TypeError):
        return 0

