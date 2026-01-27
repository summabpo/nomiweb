from apps.common.models import  Empresa

"""
Obtiene la información detallada de una empresa a partir de su ID.

Esta función consulta la base de datos para obtener los datos de una empresa especificada 
por su identificador `idemp` (ID de la empresa). Los datos se retornan en un diccionario que contiene 
información clave como el NIT, nombre, dirección, contacto y otros detalles relacionados con la empresa.

Parameters
----------
idemp : int
    El identificador único de la empresa para la cual se desean obtener los datos.

Returns
-------
dict
    Un diccionario con los datos de la empresa, donde las claves representan las diferentes propiedades 
    de la empresa (como nombre, NIT, dirección, etc.). Si algún valor no está disponible, se retorna 
    un valor predeterminado, como "No encontrado" o `0` según corresponda.

Notes
-----
- Si la empresa con el `idemp` especificado no existe en la base de datos, se generará una excepción `Empresa.DoesNotExist`.
- Los valores retornados por esta función son siempre no nulos: en caso de datos faltantes, se utiliza un valor por defecto.
"""

def datos_cliente(idemp):
    empresa_data = Empresa.objects.get(idempresa=idemp)
    
    info_cliente = {
        'idempresa': empresa_data.idempresa if empresa_data.idempresa  else 0,
        'nit': empresa_data.nit  if empresa_data.nit else 'No encontrado',
        'nombreempresa': empresa_data.nombreempresa if empresa_data.nombreempresa else 'No encontrado',
        'direccionempresa': empresa_data.direccionempresa if empresa_data.direccionempresa else 'No encontrado',
        'replegal': empresa_data.replegal if empresa_data.replegal else 'No encontrado',
        'arl': empresa_data.arl if empresa_data.arl else 'No encontrado',
        'logo': empresa_data.logo if empresa_data.logo else 'No encontrado',
        'ciudad': empresa_data.idciudad.ciudad if empresa_data.idciudad else 'No encontrado',
        'telefono': empresa_data.telefono if empresa_data.telefono else 'No encontrado',
        'email': empresa_data.email if empresa_data.email else 'No encontrado',
        'codarl': empresa_data.arl if empresa_data.arl  else 'No encontrado',
        'idcliente': empresa_data.idempresa if empresa_data.idempresa  else 0,
        'contactonomina': empresa_data.contactonomina if empresa_data.contactonomina  else 'No encontrado',
        'emailnomina': empresa_data.emailnomina if empresa_data.emailnomina else 'No encontrado',
        'contactorrhh': empresa_data.contactorrhh if empresa_data.contactorrhh else 'No encontrado',
        'emailrrhh': empresa_data.emailrrhh if empresa_data.emailrrhh else 'No encontrado',
        'contactocontab': empresa_data.contactocontab if empresa_data.contactocontab else 'No encontrado',
        'emailcontab': empresa_data.emailcontab if empresa_data.emailcontab else 'No encontrado',
        'cargocertificaciones': empresa_data.cargocertificaciones if empresa_data.cargocertificaciones else 'No encontrado',
        'firmacertificaciones': empresa_data.firmacertificaciones if empresa_data.firmacertificaciones else 'No encontrado',
        'website': empresa_data.website if  empresa_data.website else 'No encontrado',
        'metodoextras': empresa_data.metodoextras if empresa_data.metodoextras else 'No encontrado',
        'dv': empresa_data.dv if empresa_data.dv else 'No encontrado',
        'coddpto': empresa_data.idciudad.coddepartamento if empresa_data.idciudad.coddepartamento else 'No encontrado',
        'codciudad': empresa_data.idciudad.codciudad if empresa_data.idciudad.codciudad else 'No encontrado',
        'nomciudad': empresa_data.idciudad.ciudad if empresa_data.idciudad.ciudad else 'No encontrado',
        'ajustarnovedad': empresa_data.ajustarnovedad if empresa_data.ajustarnovedad else 'No encontrado',
        'realizarparafiscales': empresa_data.realizarparafiscales if empresa_data.realizarparafiscales else 'No encontrado',
        'vstccf': empresa_data.vstccf if empresa_data.vstccf else 0,
        'vstsenaicbf': empresa_data.vstsenaicbf if empresa_data.vstsenaicbf else 0,
        'ige100': empresa_data.ige100 if empresa_data.ige100 else 0,
        'slntarifapension': empresa_data.slntarifapension if empresa_data.slntarifapension else 0,
        'tipodoc': empresa_data.tipodoc if empresa_data.tipodoc else 'No encontrado',
        'codigosuc': empresa_data.codigosuc if empresa_data.codigosuc else 'No encontrado',
        'nombresuc': empresa_data.nombresuc if empresa_data.nombresuc else 'No encontrado',
        'claseaportante': empresa_data.claseaportante if empresa_data.claseaportante else 'No encontrado',
        'tipoaportante': empresa_data.tipoaportante if empresa_data.tipoaportante else 'No encontrado',
        'banco': empresa_data.banco_id if empresa_data.banco_id else 'No encontrado',
        'numcuenta': empresa_data.numcuenta if empresa_data.numcuenta else 'No encontrado',
        'tipocuenta': empresa_data.tipocuenta if empresa_data.tipocuenta else 'No encontrado',
        'pais': empresa_data.pais if empresa_data.pais else 'No encontrado',
    }

    return info_cliente




