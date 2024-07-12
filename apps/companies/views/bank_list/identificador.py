def obtener_numero_documento(tipo_texto):
    tipo_documento = {
        'NIT': '01',
        'CC': '02',
        'TI': '03',
        'CE': '04',
        'PA': '05',
        # 'Tarjeta Seguro Social': '06',
        # 'Nit Menores': '07'
    }
    # Verificar si el tipo de documento está en el diccionario
    if tipo_texto in tipo_documento:
        return tipo_documento[tipo_texto]
    else:
        return None  