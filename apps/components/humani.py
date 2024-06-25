
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

