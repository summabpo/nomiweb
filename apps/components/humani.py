
def format_value(value):
    if value is None:
        return '0'
    try:
        return "{:,}".format(int(value)).replace(",", ".")
    except ValueError:
        return str(value)
