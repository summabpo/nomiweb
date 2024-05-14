#models
from apps.employees.models import  Certificaciones, Tipocontrato, Empresa
from apps.employees.models import Crearnomina, Nomina, Contratos, Contratosemp
from django.db.models import Sum, F, Value, CharField
from django.db.models.functions import Concat

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

# def datos_empleado(id_empleado=3863):
#     contrato = Contratos.objects.select_related('tipocontrato').get(idcontrato=id_empleado)
    
#     empleado = Contratosemp.objects.annotate(
#         nombre_letras=Concat('pnombre', Value(' '), 'snombre', Value(' '), 'papellido', Value(' '), 'sapellido', output_field=CharField())
#     ).get(idempleado=contrato.idempleado_id)
    
#     info_empleado = {
#         'nombre_completo': empleado.nombre_letras,
#         'fechainiciocontrato': contrato.fechainiciocontrato,
#         'cargo': contrato.cargo,
#         'tipo_contrato': contrato.tipocontrato.tipocontrato,
#         'docidentidad': empleado.docidentidad,
#         'salario': contrato.salario,
#         'idc': contrato.idcontrato,
#         'ide': empleado.idempleado
#     }
#     return info_empleado
def datos_empleado(id_contrato=15):
    
    contrato = Contratos.objects.get(idcontrato=id_contrato)
    empleado = Contratosemp.objects.filter(idempleado=contrato.idempleado_id).annotate(
        nombre_letras=Concat(F('pnombre'), Value(' '), F('snombre'), Value(' '), 
                                F('papellido'), Value(' '), F('sapellido'), output_field=CharField())
                                ).values('nombre_letras').first()
        
    info_empleado = {
        'nombre_completo': empleado['nombre_letras'], 
        'fechainiciocontrato': contrato.fechainiciocontrato,
        'cargo': contrato.cargo, 
        'tipo_contrato': contrato.tipocontrato.idtipocontrato,
        'nombre_contrato': contrato.tipocontrato.tipocontrato,
        'docidentidad': contrato.idempleado.docidentidad ,
        'salario': contrato.salario,
        'idc': contrato.idcontrato,
        'ide': contrato.idempleado_id
    }
    return info_empleado
