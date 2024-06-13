from apps.employees.models import  Empresa


def datos_cliente():
    empresa_data = Empresa.objects.filter(idempresa=1).values().first()

    if empresa_data:
        info_cliente = {
            'nombre_empresa': empresa_data['nombreempresa'],
            'nombre_rrhh': empresa_data['contactorrhh'],
            'nit_empresa': empresa_data['nit'],
            'direccion_empresa': empresa_data['direccionempresa'],
            'ciudad_empresa': empresa_data['ciudad'],
            'telefono_empresa': empresa_data['telefono'],
            'website_empresa': empresa_data['website'],
            'email_empresa': empresa_data['email'],
            'logo_empresa': empresa_data['logo'],
            'id_cliente': empresa_data['idcliente'],
            'cargo_certificaciones': empresa_data['cargocertificaciones'],
            'firma_certificaciones': empresa_data['firmacertificaciones'],
            'emailrrhh': empresa_data['emailrrhh']
            
        }
    else:
        # Manejar el caso donde no se encuentra la empresa con el id especificado
        info_cliente = {}

    return info_cliente



