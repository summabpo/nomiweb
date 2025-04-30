from django.db.models.functions import Concat
from django.db.models import F, Value, CharField
from apps.common.models import Contratos, Contratosemp

"""
    las Función que maneja la obtención de los datos completos de un empleado a partir del contrato asociado.

    Esta función realiza una consulta optimizada para obtener los datos del empleado basándose en un contrato
    específico. Se utilizan funciones de anotación para concatenar los nombres del empleado en una sola cadena
    y se obtiene información adicional sobre el contrato del empleado.

    Parameters
    ----------
    id_contrato : int, opcional
        El ID del contrato del empleado. Por defecto es 15 pero este valor es solo para evisar erores .

    Returns
    -------
    dict
        Diccionario con los datos del empleado y el contrato, incluyendo nombre completo, fechas de inicio y fin
        del contrato, cargo, tipo de contrato, documento de identidad, salario, entre otros.

    Notes
    -----
    - Esta función realiza una consulta en la base de datos usando el ID del contrato.
    - Se realiza una concatenación de los campos `pnombre`, `snombre`, `papellido` y `sapellido` del empleado para 
      formar el nombre completo.
    - Si no se encuentra el contrato con el ID proporcionado, se generará una excepción `DoesNotExist`.

    See Also
    --------
    - `Contratos`
    - `Contratosemp`
"""

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
