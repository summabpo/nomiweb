from apps.employees.models import  Empresa

from apps.employees.models import Empresa

def datos_cliente():
    empresa_data = Empresa.objects.filter(idempresa=1).values().first()

    # Inicializar la información del cliente con valores por defecto
    info_cliente = {
        'idempresa': empresa_data['idempresa'] if empresa_data and 'idempresa' in empresa_data else 0,
        'nit': empresa_data['nit'] if empresa_data and 'nit' in empresa_data else 'No encontrado',
        'nombreempresa': empresa_data['nombreempresa'] if empresa_data and 'nombreempresa' in empresa_data else 'No encontrado',
        'direccionempresa': empresa_data['direccionempresa'] if empresa_data and 'direccionempresa' in empresa_data else 'No encontrado',
        'replegal': empresa_data['replegal'] if empresa_data and 'replegal' in empresa_data else 'No encontrado',
        'arl': empresa_data['arl'] if empresa_data and 'arl' in empresa_data else 'No encontrado',
        'logo': empresa_data['logo'] if empresa_data and 'logo' in empresa_data else 'No encontrado',
        'ciudad': empresa_data['ciudad'] if empresa_data and 'ciudad' in empresa_data else 'No encontrado',
        'telefono': empresa_data['telefono'] if empresa_data and 'telefono' in empresa_data else 'No encontrado',
        'email': empresa_data['email'] if empresa_data and 'email' in empresa_data else 'No encontrado',
        'codarl': empresa_data['codarl'] if empresa_data and 'codarl' in empresa_data else 'No encontrado',
        'idcliente': empresa_data['idcliente'] if empresa_data and 'idcliente' in empresa_data else 0,
        'bdatos': empresa_data['bdatos'] if empresa_data and 'bdatos' in empresa_data else 'No encontrado',
        'contactonomina': empresa_data['contactonomina'] if empresa_data and 'contactonomina' in empresa_data else 'No encontrado',
        'emailnomina': empresa_data['emailnomina'] if empresa_data and 'emailnomina' in empresa_data else 'No encontrado',
        'contactorrhh': empresa_data['contactorrhh'] if empresa_data and 'contactorrhh' in empresa_data else 'No encontrado',
        'emailrrhh': empresa_data['emailrrhh'] if empresa_data and 'emailrrhh' in empresa_data else 'No encontrado',
        'contactocontab': empresa_data['contactocontab'] if empresa_data and 'contactocontab' in empresa_data else 'No encontrado',
        'emailcontab': empresa_data['emailcontab'] if empresa_data and 'emailcontab' in empresa_data else 'No encontrado',
        'cargocertificaciones': empresa_data['cargocertificaciones'] if empresa_data and 'cargocertificaciones' in empresa_data else 'No encontrado',
        'firmacertificaciones': empresa_data['firmacertificaciones'] if empresa_data and 'firmacertificaciones' in empresa_data else 'No encontrado',
        'website': empresa_data['website'] if empresa_data and 'website' in empresa_data else 'No encontrado',
        'metodoextras': empresa_data['metodoextras'] if empresa_data and 'metodoextras' in empresa_data else 'No encontrado',
        'dv': empresa_data['dv'] if empresa_data and 'dv' in empresa_data else 'No encontrado',
        'coddpto': empresa_data['coddpto'] if empresa_data and 'coddpto' in empresa_data else 'No encontrado',
        'codciudad': empresa_data['codciudad'] if empresa_data and 'codciudad' in empresa_data else 'No encontrado',
        'nomciudad': empresa_data['nomciudad'] if empresa_data and 'nomciudad' in empresa_data else 'No encontrado',
        'ajustarnovedad': empresa_data['ajustarnovedad'] if empresa_data and 'ajustarnovedad' in empresa_data else 'No encontrado',
        'realizarparafiscales': empresa_data['realizarparafiscales'] if empresa_data and 'realizarparafiscales' in empresa_data else 'No encontrado',
        'vstccf': empresa_data['vstccf'] if empresa_data and 'vstccf' in empresa_data else 0,
        'vstsenaicbf': empresa_data['vstsenaicbf'] if empresa_data and 'vstsenaicbf' in empresa_data else 0,
        'ige100': empresa_data['ige100'] if empresa_data and 'ige100' in empresa_data else 0,
        'slntarifapension': empresa_data['slntarifapension'] if empresa_data and 'slntarifapension' in empresa_data else 0,
        'tipodoc': empresa_data['tipodoc'] if empresa_data and 'tipodoc' in empresa_data else 'No encontrado',
        'codigosuc': empresa_data['codigosuc'] if empresa_data and 'codigosuc' in empresa_data else 'No encontrado',
        'nombresuc': empresa_data['nombresuc'] if empresa_data and 'nombresuc' in empresa_data else 'No encontrado',
        'claseaportante': empresa_data['claseaportante'] if empresa_data and 'claseaportante' in empresa_data else 'No encontrado',
        'tipoaportante': empresa_data['tipoaportante'] if empresa_data and 'tipoaportante' in empresa_data else 'No encontrado',
        'banco': empresa_data['banco'] if empresa_data and 'banco' in empresa_data else 'No encontrado',
        'numcuenta': empresa_data['numcuenta'] if empresa_data and 'numcuenta' in empresa_data else 'No encontrado',
        'tipocuenta': empresa_data['tipocuenta'] if empresa_data and 'tipocuenta' in empresa_data else 'No encontrado',
        'pais': empresa_data['pais'] if empresa_data and 'pais' in empresa_data else 'No encontrado',
    }

    return info_cliente




