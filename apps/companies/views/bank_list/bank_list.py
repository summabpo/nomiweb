from django.shortcuts import render
from apps.common.models  import Nomina , Bancos
from apps.components.humani import format_value
from apps.components.format import formttex , formtnun
from django.http import JsonResponse
from django.http import HttpResponse
from apps.components.datacompanies import datos_cliente 
import io
from datetime import datetime

from django.shortcuts import get_object_or_404
from .identificador import obtener_numero_documento

from django.db.models import Sum, Count, Q

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('company')
def bank_list_get(request,idnomina):
    """
        Recupera el resumen de los pagos asociados a una nómina específica.

        Esta vista obtiene información relacionada con los pagos de una nómina, como el banco y el número de cuenta,
        y un desglose de los registros de empleados asociados con las cuentas de ahorro y corriente.

        Parameters
        ----------
        request : HttpRequest
            Objeto de solicitud HTTP que contiene el parámetro 'id_nomina' con el identificador de la nómina.

        Returns
        -------
        JsonResponse
            Respuesta en formato JSON con los detalles del banco, número de cuenta, 
            cantidad de registros con cuenta de ahorro y corriente, y el total de pagos realizados.

        See Also
        --------
        Nomina : Modelo que representa los registros de pago de empleados.
        Bancos : Modelo que representa los datos bancarios.
        format_value : Función que formatea valores monetarios.
        

        Notes
        -----
        El usuario debe estar autenticado y tener el rol `'company'` para acceder a esta vista.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    dataempresa = datos_cliente(idempresa)
    pas = False

    # 🔹 Datos del banco (1 sola consulta)
    banco_nota = "Data no encontrada"
    num_cuenta = dataempresa.get('numcuenta', 'Data no encontrada')

    banco_id = dataempresa.get('banco')
    if banco_id:
        banco = Bancos.objects.filter(idbanco=banco_id).only('nombanco', 'digchequeo').first()
        if banco:
            banco_nota = f"{banco.nombanco} - {banco.digchequeo}"
            pas = True

    # 🔹 Query base optimizada
    nominas = Nomina.objects.filter(idnomina=idnomina).select_related(
        'idcontrato__idempleado'
    )

    # 🔹 SUMA TOTAL (en BD)
    suma_total_pagos = nominas.aggregate(total=Sum('valor'))['total'] or 0

    # 🔹 CONTAR EMPLEADOS ÚNICOS POR TIPO DE CUENTA
    cuentas = nominas.values(
        'idcontrato__idempleado__docidentidad',
        'idcontrato__formapago'
    ).distinct()

    count_cuenta_1 = 0
    count_cuenta_2 = 0

    for c in cuentas:
        if c['idcontrato__formapago'] == '1':
            count_cuenta_1 += 1
        else:
            count_cuenta_2 += 1

    data = {
        'banco': banco_nota,
        'cuenta': num_cuenta,
        'registros_con_cuenta': count_cuenta_1,
        'registros_sin_cuenta': count_cuenta_2,
        'valor_pagos': format_value(suma_total_pagos),
        'pass': pas,
        'selected_nomina':idnomina
    }

    
    print(data)
    return render(request, './companies/partials/flat_bank.html', {'data': data})


@login_required
@role_required('company')
def bank_file(request,idnomina):
    """
    Genera un archivo de texto plano con los pagos de la nómina.

    Esta vista construye un archivo de texto con la información de los pagos realizados en una nómina específica, 
    estructurado conforme al formato requerido por el banco, en este caso, Davivienda.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene el parámetro 'idnomina' con el identificador de la nómina.

    Returns
    -------
    HttpResponse
        Respuesta que contiene el archivo de texto generado para ser descargado.

    See Also
    --------
    Nomina : Modelo que representa los registros de pago de empleados.
    Bancos : Modelo que representa los datos bancarios.
    obtener_numero_documento : Función que obtiene el número de documento de un empleado.
    formttex, formtnun : Funciones que formatean los valores de acuerdo al formato requerido por el archivo.


    Notes
    -----
    El usuario debe estar autenticado y tener el rol `'company'` para acceder a esta vista.
    El archivo generado tiene el formato requerido por Davivienda y será descargado por el navegador.
    """

    # Obtener la fecha actual
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    fecha_actual = datetime.now()

    # Formatear la fecha como AAAAMMDD
    fecha_formateada = fecha_actual.strftime("%Y%m%d")
    compects = []
    acumulados = {}
    suma_total_pagos = 0
    count_cuenta_1 = 0
    compectos = Nomina.objects.filter(idnomina=idnomina).order_by('idcontrato__idempleado__papellido')  
    
    
    for data in compectos:
            
        docidentidad = data.idcontrato.idempleado.docidentidad

        if docidentidad not in acumulados:
            
            
            acumulados[docidentidad] = {
                'cc':data.idcontrato.idempleado.docidentidad,
                'tipecc':data.idcontrato.idempleado.tipodocident.codigo,
                'numcuenta': data.idcontrato.cuentanomina,
                'banco': (
                        Bancos.objects.filter(nombanco=data.idcontrato.bancocuenta)
                        .values_list('digchequeo', flat=True)
                        .first()
                        if data.idcontrato.bancocuenta else ""
                    ),
                'cuenta': data.idcontrato.tipocuentanomina,
                'pago': 0,
                'pasos': 1 if data.idcontrato.formapago == '1' else 2
            }
        
            
            if acumulados[docidentidad]['pasos'] == 1:
                count_cuenta_1 += 1
                
        acumulados[docidentidad]['pago'] += data.valor      
            

            
        suma_total_pagos += data.valor
    
    compects = list(acumulados.values())
    
    # Generar el código de la empresa
    strrc = 'RC'
    dataempresa = datos_cliente(idempresa)
    strrc += formttex(dataempresa['nit'] + dataempresa['dv'], 16)
    strrc += formttex('NOMI', 4)
    strrc += formttex('NOMI', 4)
    strrc += formttex(dataempresa['numcuenta'], 16)
    strrc += formttex('CC', 2)
    strrc += formttex(str(dataempresa['banco']), 6)
    strrc += formtnun(suma_total_pagos, 18)
    strrc += formttex(str(count_cuenta_1), 6)
    strrc += formttex(fecha_formateada, 8)
    strrc += formttex('000000', 6)
    strrc += formttex('0', 4)
    strrc += formttex('9999', 4)
    strrc += formttex('0', 8)
    strrc += formttex('0', 6)
    strrc += formttex('0', 2)
    strrc += formttex('01', 2)
    strrc += formttex('0', 12)
    strrc += formttex('0', 4)
    strrc += formttex('0', 40)
    strrc += '\n'
    
    for data in compects:
        strrc += 'TR'
        strrc += formttex(str(data['cc']), 16)
        strrc += formttex('0', 16)
        strrc += formttex(data['numcuenta'], 16)
        
        if data['cuenta'] == 'ahorros':
            strrc += formttex('CA', 2)
        elif data['cuenta'] == 'corriente':
            strrc += formttex('CC', 2)
        else:
            strrc += formttex('OP', 2)
    
        
        strrc += formttex(str(data['banco']), 6)
        strrc += formtnun(data['pago'], 18)
        strrc += formttex('0', 6)
        strrc += formttex(data['tipecc'], 2)
        strrc += formttex('0', 1)
        strrc += formttex('9999', 4)
        strrc += formttex('0', 40)
        strrc += formttex('0', 18)
        strrc += formttex('0', 8)
        strrc += formttex('0', 4)
        strrc += formttex('0', 4)
        strrc += formttex('0', 7)
        strrc += '\n'

    #Crear y escribir en el archivo
    buffer = io.BytesIO()
    buffer.write(strrc.encode())
    buffer.seek(0)

    filename = f'archivo_plano_davivienda_{idnomina}_{fecha_formateada}.txt'
    #Devolver una respuesta de descarga
    response = HttpResponse(buffer, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'

    return response
    #return HttpResponse(strrc)