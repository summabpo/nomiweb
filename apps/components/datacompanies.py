from apps.employees.models import  Empresa


def datos_cliente():
    empresa_data = Empresa.objects.filter(idempresa=1).values().first()

    if empresa_data:
        info_cliente = {
            'idempresa': empresa_data['idempresa'],
            'nit': empresa_data['nit'],
            'nombreempresa': empresa_data['nombreempresa'],
            'direccionempresa': empresa_data['direccionempresa'],
            'replegal': empresa_data['replegal'],
            'arl': empresa_data['arl'],
            'logo': empresa_data['logo'],
            'ciudad': empresa_data['ciudad'],
            'telefono': empresa_data['telefono'],
            'email': empresa_data['email'],
            'codarl': empresa_data['codarl'],
            'idcliente': empresa_data['idcliente'],
            'bdatos': empresa_data['bdatos'],
            'contactonomina': empresa_data['contactonomina'],
            'emailnomina': empresa_data['emailnomina'],
            'contactorrhh': empresa_data['contactorrhh'],
            'emailrrhh': empresa_data['emailrrhh'],
            'contactocontab': empresa_data['contactocontab'],
            'emailcontab': empresa_data['emailcontab'],
            'cargocertificaciones': empresa_data['cargocertificaciones'],
            'firmacertificaciones': empresa_data['firmacertificaciones'],
            'website': empresa_data['website'],
            'metodoextras': empresa_data['metodoextras'],
            'dv': empresa_data['dv'],
            'coddpto': empresa_data['coddpto'],
            'codciudad': empresa_data['codciudad'],
            'nomciudad': empresa_data['nomciudad'],
            'ajustarnovedad': empresa_data['ajustarnovedad'],
            'realizarparafiscales': empresa_data['realizarparafiscales'],
            'vstccf': empresa_data['vstccf'],
            'vstsenaicbf': empresa_data['vstsenaicbf'],
            'ige100': empresa_data['ige100'],
            'slntarifapension': empresa_data['slntarifapension'],
            'tipodoc': empresa_data['tipodoc'],
            'codigosuc': empresa_data['codigosuc'],
            'nombresuc': empresa_data['nombresuc'],
            'claseaportante': empresa_data['claseaportante'],
            'tipoaportante': empresa_data['tipoaportante'],
            'banco': empresa_data['banco'],
            'numcuenta': empresa_data['numcuenta'],
            'tipocuenta': empresa_data['tipocuenta'],
            'pais': empresa_data['pais'],
        }
    else:
        # Manejar el caso donde no se encuentra la empresa con el id especificado
        info_cliente = []

    return info_cliente



