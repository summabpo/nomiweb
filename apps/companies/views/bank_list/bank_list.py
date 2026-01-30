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
    #suma_total_pagos = nominas.aggregate(total=Sum('valor'))['total'] or 0
    suma_total_pagos = 0 
    for data in nominas:
        if data.idcontrato.bancocuenta : 
            suma_total_pagos += data.valor 
    
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

    return render(request, './companies/partials/flat_bank.html', {'data': data})


def fmt_num(valor, largo):
    """Rellena con ceros a la izquierda y solo números"""
    valor = str(valor).replace('.', '').replace(',', '')
    return valor.zfill(largo)[:largo]


def fmt_str_ceros(texto, largo):
    """Texto alineado a la izquierda, relleno con espacios"""
    texto = str(texto) if texto else ''
    return texto.ljust(largo)[:largo]


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
            
            if data.idcontrato.bancocuenta :
                acumulados[docidentidad] = {
                    'cc':data.idcontrato.idempleado.docidentidad,
                    'tipecc':obtener_numero_documento(data.idcontrato.idempleado.tipodocident.codigo),
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
                
        
        
            

        if data.idcontrato.bancocuenta : 
            acumulados[docidentidad]['pago'] += data.valor   
            suma_total_pagos += data.valor
    
    compects = list(acumulados.values())
    
    dataempresa = datos_cliente(idempresa)
    
    
    
    codigo = Bancos.objects.get(idbanco  = dataempresa['banco']).digchequeo
    
    
    # Generar el código de la empresa
    strrc = ''
    strrc2 = ''
    rc1 = ''

    
    
    
    for data in compects:
        tr = ''

        tr += 'TR'
        tr += fmt_num(data['cc'], 16)      # Documento beneficiario
        tr += fmt_num(0, 16)               # Referencia
        tr += fmt_num(data['numcuenta'], 16)

        
        if data['banco'] == '5':
            tr += fmt_str_ceros('DP', 2)
        else : 
            # Tipo de producto destino
            if data['cuenta'] == 'ahorros':
                tr += fmt_str_ceros('CA', 2)
            elif data['cuenta'] == 'corriente':
                tr += fmt_str_ceros('CC', 2)
            else:
                tr += fmt_str_ceros('CA', 2)
            
        
        
        if data['banco'] == '5' : 
            tr += fmt_num(51, 6)
        else:
            # Código ACH del banco destino
            tr += fmt_num(data['banco'], 6)

        # Valor en centavos
        valor_centavos = int(round(data['pago'] * 100))
        tr += fmt_num(valor_centavos, 18)

        tr += fmt_num(0, 6)  # Talón

        # Tipo de documento beneficiario (01 CC, 02 CE, 03 NIT, etc.)
        tr += fmt_num(data['tipecc'], 2)

        # ✅ Validar ACH = 1
        tr += fmt_num(1, 1)

        tr += fmt_num(9999, 4)  # Resultado

        tr += fmt_num(0, 40)  # Mensaje respuesta
        tr += fmt_num(0, 18)  # Valor acumulado
        tr += fmt_num(0, 8)   # Fecha aplicación
        tr += fmt_num(0, 4)   # Oficina
        tr += fmt_num(0, 4)   # Motivo devolución
        tr += fmt_num(0, 7)   # Campo futuro

        assert len(tr) == 170
        
        if fmt_num(data['banco'], 6) != '000000':
            strrc2 += tr + '\n'
            count_cuenta_1 += 1

    
    rc1 += 'RC'
    rc1 += fmt_num(dataempresa['nit'] + dataempresa['dv'], 16)
    #rc1 += '0000008904043831'
    rc1 += fmt_str_ceros('NOMI', 4)
    rc1 += fmt_str_ceros('NOMI', 4)
    rc1 += fmt_num('0550116100064058', 16)

    # Tipo de cuenta empresa (AHO = CA / CORR = CC)
    rc1 += fmt_str_ceros('CC', 2)

    # Código ACH banco empresa
    rc1 += fmt_num(codigo, 6)

    # Valor total en CENTAVOS
    total_centavos = int(round(suma_total_pagos * 100))
    rc1 += fmt_num(total_centavos, 18)

    # Cantidad de registros TR
    rc1 += fmt_num(count_cuenta_1, 6)

    rc1 += fmt_num(fecha_formateada, 8)   # YYYYMMDD
    rc1 += fmt_num('000000', 6)          # Hora proceso
    rc1 += fmt_num('0000', 4)         # Operador
    rc1 += fmt_num('9999', 4)
    rc1 += fmt_num(0, 8)                 # Fecha generación
    rc1 += fmt_num(0, 6)                 # Hora generación
    rc1 += fmt_num(0, 2)

    # ✅ TIPO IDENTIFICACIÓN EMPRESA = 03 (NIT)
    rc1 += fmt_num('03', 2)

    rc1 += fmt_num(0, 12)  # Cliente Davivienda
    rc1 += fmt_num(0, 4)   # Oficina
    rc1 += fmt_num(0, 40)  # Campo futuro

    assert len(rc1) == 170
    
    
    strrc += rc1 + '\n' + strrc2
    
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
    
    
    
    
    
    