# models
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

def datos_empleado():
    #DATOS EMPLEADO
    idc=3863
    idempleado_id = Contratos.objects.get(idcontrato=idc).idempleado_id
    ide = idempleado_id
    empleado = Contratosemp.objects.filter(idempleado=ide).annotate(nombre_letras=Concat(

        F('pnombre'),
        Value(' '),
        F('snombre'),
        Value(' '),
        F('papellido'),
        Value(' '),
        F('sapellido'),
        output_field=CharField()
    )).values('nombre_letras').first()
    nombre_completo = empleado['nombre_letras']
    fechainiciocontrato = Contratos.objects.get(idcontrato=idc).fechainiciocontrato
    cargo = Contratos.objects.get(idcontrato=idc).cargo
    tipo_contrato = Contratos.objects.get(idcontrato=idc).tipocontrato
    nombre_contrato = Tipocontrato.objects.get(idtipocontrato=tipo_contrato).tipocontrato
    docidentidad = Contratosemp.objects.get(idempleado=ide).docidentidad
    salario = Contratos.objects.get(idcontrato=idc).salario


    info_empleado = {
        'nombre_completo': nombre_completo,
        'fechainiciocontrato': fechainiciocontrato,
        'cargo': cargo,
        'tipo_contrato': tipo_contrato,
        'nombre_contrato': nombre_contrato,
        'docidentidad': docidentidad,
        'salario': salario,
        'idc': idc,
        'ide': ide
    }
    return info_empleado

