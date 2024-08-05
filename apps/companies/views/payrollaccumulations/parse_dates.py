from datetime import datetime, date

def parse_dates(start_date, end_date):
    """
    Convierte las fechas dadas en cadenas y devuelve el año y mes de cada una.
    
    Converts the given dates to extract year and month for each.

    :param start_date: Fecha de inicio (string o datetime.date)
    :param end_date: Fecha de fin (string o datetime.date)
    :return: Tupla con (start_year, start_month, end_year, end_month)
    
    :param start_date: Start date (string or datetime.date)
    :param end_date: End date (string or datetime.date)
    :return: Tuple with (start_year, start_month, end_year, end_month)
    """
    # Diccionario de nombres de meses en español
    # Dictionary of month names in Spanish
    month_names = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    # Convertir a cadenas si las fechas son objetos datetime.date
    # Convert to strings if dates are datetime.date objects
    if isinstance(start_date, date):
        start_date_str = start_date.strftime('%Y-%m-%d')
    else:
        start_date_str = str(start_date)

    if isinstance(end_date, date):
        end_date_str = end_date.strftime('%Y-%m-%d')
    else:
        end_date_str = str(end_date)

    # Inicializar variables para el año y el mes
    # Initialize variables for year and month
    start_year = start_month_name = end_year = end_month_name = None
    
    # Convertir las fechas si son cadenas
    # Convert the dates if they are strings
    if start_date_str:
        try:
            start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            start_year = start_date_obj.year
            start_month_number = start_date_obj.month
            start_month_name = month_names.get(start_month_number, 'Unknown Month')
        except ValueError:
            print("El formato de start_date es inválido")
            # Handle invalid start_date format
            print("The format of start_date is invalid")
    
    if end_date_str:
        try:
            end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            end_year = end_date_obj.year
            end_month_number = end_date_obj.month
            end_month_name = month_names.get(end_month_number, 'Unknown Month')
        except ValueError:
            print("El formato de end_date es inválido")
            # Handle invalid end_date format
            print("The format of end_date is invalid")
    
    return start_year, start_month_name, end_year, end_month_name

# Ejemplo de uso:
# start_date = '2024-08-01'
# end_date = '2024-08-31'
# start_year, start_month, end_year, end_month = parse_dates(start_date, end_date)
# print(f"Start Date: Año {start_year}, Mes {start_month}")
# print(f"End Date: Año {end_year}, Mes {end_month}")
