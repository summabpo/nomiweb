from django.db.models.functions import Concat
from django.db.models import F, Value, CharField
from apps.common.models import Contratos, Contratosemp

def datos_empleado(id_contrato=15):
    
    contrato = Contratos.objects.get(idcontrato=id_contrato)
    empleado = Contratosemp.objects.filter(idempleado=contrato.idempleado_id).annotate(
        nombre_letras=Concat(F('pnombre'), Value(' '), F('snombre'), Value(' '), 
                                F('papellido'), Value(' '), F('sapellido'), output_field=CharField())
                                ).values('nombre_letras').first()
        
    info_empleado = {
        'nombre_completo': empleado['nombre_letras'], 
        'fechainiciocontrato': contrato.fechainiciocontrato,
        'fechafincontrato': contrato.fechafincontrato,
        'cargo': contrato.cargo, 
        'tipo_contrato': contrato.tipocontrato.idtipocontrato,
        'nombre_contrato': contrato.tipocontrato.tipocontrato,
        'docidentidad': contrato.idempleado.docidentidad ,
        'salario': contrato.salario,
        'idc': contrato.idcontrato,
        'ide': contrato.idempleado_id
    }
    return info_empleado


def datos_empleado2(id_empleado):
    try:
        empleado = Contratosemp.objects.only('pnombre', 'snombre', 'papellido', 'sapellido', 'email','fotografiaempleado').get(idempleado=id_empleado)
        if empleado.fotografiaempleado and hasattr(empleado.fotografiaempleado, 'url'):
            url_foto = empleado.fotografiaempleado.url
        else:
            url_foto = None
                
        nombre_completo = f"{empleado.pnombre} {empleado.papellido}"
        info_empleado = {
            'nombre_completo': nombre_completo.strip(),  # Elimina espacios en blanco adicionales
            'email': empleado.email,
            'fotografiaempleado': url_foto ,
        }
    except Contratosemp.DoesNotExist:
        info_empleado = {
            'nombre_completo': '',
            'email': '',
            'fotografiaempleado': '',
        }
    
    return info_empleado


    try:
        empleado = Contratosemp.objects.annotate(
            nombre_letras=Concat(
                F('pnombre'), Value(' '), F('snombre'), Value(' '), 
                F('papellido'), Value(' '), F('sapellido'), 
                output_field=CharField()
            )
        ).only('nombre_letras', 'email').get(idempleado=id_empleado)
        
        info_empleado = {
            'nombre_completo': empleado.nombre_letras,
            'email': empleado.email,
        }
    except Contratosemp.DoesNotExist:
        info_empleado = {
            'nombre_completo': '',
            'email': '',
        }
    
    return info_empleado