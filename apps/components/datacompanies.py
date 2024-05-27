from apps.employees.models import  Certificaciones, Tipocontrato, Empresa


def datos_cliente():
    nombre_empresa = Empresa.objects.get(idempresa=1).nombreempresa
    nombre_rrhh = Empresa.objects.get(idempresa=1).contactorrhh
    cargo_certificaciones = Empresa.objects.get(idempresa=1).cargocertificaciones
    nit_empresa = Empresa.objects.get(idempresa=1).nit
    direccion_empresa = Empresa.objects.get(idempresa=1).direccionempresa
    ciudad_empresa = Empresa.objects.get(idempresa=1).ciudad
    telefono_empresa = Empresa.objects.get(idempresa=1).telefono
    website_empresa = Empresa.objects.get(idempresa=1).website
    email_empresa = Empresa.objects.get(idempresa=1).email
    logo_empresa = Empresa.objects.get(idempresa=1).logo
    id_cliente = Empresa.objects.get(idempresa=1).idcliente
    firma_certificaciones = Empresa.objects.get(idempresa=1).firmacertificaciones

    info_cliente = {
        'nombre_empresa': nombre_empresa,
        'nombre_rrhh': nombre_rrhh,
        'nit_empresa': nit_empresa,
        'direccion_empresa': direccion_empresa,
        'ciudad_empresa': ciudad_empresa,
        'telefono_empresa': telefono_empresa,
        'website_empresa': website_empresa,
        'email_empresa': email_empresa,
        'logo_empresa': logo_empresa,
        'id_cliente': id_cliente,
        'cargo_certificaciones': cargo_certificaciones,
        'firma_certificaciones': firma_certificaciones
    }
    return info_cliente

