from django.shortcuts import render
from apps.companies.models import Nomina , Bancos
from apps.components.humani import format_value
from apps.components.format import formttex , formtnun
from django.http import JsonResponse
from django.http import HttpResponse
from apps.components.datacompanies import datos_cliente 
import io
from datetime import datetime

from django.shortcuts import get_object_or_404
from .identificador import obtener_numero_documento



from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('entrepreneur')
def bank_list_get(request):
    count_cuenta_1 = 0
    count_cuenta_2 = 0
    suma_total_pagos = 0
    acumulados = {}
    id_nomina = request.GET.get('id_nomina')  
    dataempresa = datos_cliente()
    compectos = Nomina.objects.filter(idnomina=id_nomina)
    
    banco = Bancos.objects.get(digchequeo =dataempresa['banco'] )
    
    
    for data in compectos:
            
        docidentidad = data.idempleado.docidentidad
    
        if docidentidad not in acumulados:
            acumulados[docidentidad] = {
                'cuenta': 1 if data.idcontrato.formapago == '1' else 2
            }

            if acumulados[docidentidad]['cuenta'] == 1:
                count_cuenta_1 += 1
            elif acumulados[docidentidad]['cuenta'] == 2:
                count_cuenta_2 += 1
            
        suma_total_pagos += data.valor
        
    
    data = {
            'banco': f"{banco.nombanco} - {banco.digchequeo} ",
            'cuenta': dataempresa['numcuenta'],
            'registros_con_cuenta': count_cuenta_1,
            'valor_pagos': format_value(suma_total_pagos),
            'registros_sin_cuenta': count_cuenta_2
        }
    
    return JsonResponse(data)

@login_required
@role_required('entrepreneur')
def bank_file(request,idnomina):
    # Obtener la fecha actual
    fecha_actual = datetime.now()

    # Formatear la fecha como AAAAMMDD
    fecha_formateada = fecha_actual.strftime("%Y%m%d")
    compects = []
    acumulados = {}
    suma_total_pagos = 0
    count_cuenta_1 = 0
    compectos = Nomina.objects.filter(idnomina=idnomina).order_by('idempleado__papellido')  
    
    
    for data in compectos:
            
        docidentidad = data.idempleado.docidentidad

        if docidentidad not in acumulados:
            acumulados[docidentidad] = {
                'cc':data.idempleado.docidentidad,
                'tipecc':data.idempleado.tipodocident,
                'numcuenta': data.idcontrato.cuentanomina,
                'banco':  get_object_or_404(Bancos, nombanco=data.idcontrato.bancocuenta).digchequeo,
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
    dataempresa = datos_cliente()
    strrc += formttex(dataempresa['nit'] + dataempresa['dv'], 16)
    strrc += formttex('NOMI', 4)
    strrc += formttex('NOMI', 4)
    strrc += formttex(dataempresa['numcuenta'], 16)
    strrc += formttex('CC', 2)
    strrc += formttex(dataempresa['banco'], 6)
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
        strrc += formttex(obtener_numero_documento(data['tipecc']), 2)
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