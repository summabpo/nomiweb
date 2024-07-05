from django.shortcuts import render
from apps.companies.models import Nomina
import random
from datetime import datetime, timedelta

def payrollsheet(request):
    nominas = Nomina.objects.select_related('idnomina').values_list('idnomina__nombrenomina', 'idnomina').distinct().order_by('-idnomina')
    compects = []  # Define compects here
    acumulados = {}
    
    selected_nomina = request.GET.get('nomina')
    if selected_nomina:
        compectos = Nomina.objects.filter(idnomina = selected_nomina , idempleado__docidentidad = 1070750750  )
               
        for data in compectos:
            docidentidad = data.idempleado.docidentidad
            if docidentidad not in acumulados:
                acumulados[docidentidad] = {
                    'documento': docidentidad,
                    'nombre': f"{data.idempleado.papellido} {data.idempleado.sapellido} {data.idempleado.pnombre} {data.idempleado.snombre}",
                    
                    'basico': data.valor if data.idconcepto.sueldobasico == 1 else 0 ,
                    'tpte': data.valor if data.idconcepto.auxtransporte == 1 else 0 ,
                    'extras': data.valor if data.idconcepto.extras == 1 else 0 ,
                    'otros1':0 ,
                    'ingresos': data.valor if data.valor > 0 else 0,
                    'neto': data.valor,
                    'aportess':data.valor if data.idconcepto.aportess == 1 else 0 ,
                    
                }
            else:
                acumulados[docidentidad]['neto'] += data.valor
                
                # Sumar el valor al campo basico si la condición se cumple
                if data.idconcepto.sueldobasico == 1:
                    acumulados[docidentidad]['basico'] += data.valor
                
                # Sumar el valor al campo tpte si la condición se cumple
                if data.idconcepto.auxtransporte == 1:
                    acumulados[docidentidad]['tpte'] += data.valor
                    
                # Sumar el valor al campo extras si la condición se cumple
                if data.idconcepto.extras == 1:
                    acumulados[docidentidad]['extras'] += data.valor
                    
                # Sumar el valor al campo ingresos solo si es positivo
                if data.valor > 0:
                    acumulados[docidentidad]['ingresos'] += data.valor
                    
                # Sumar el valor al campo extras si la condición se cumple
                if data.idconcepto.aportess == 1:
                    acumulados[docidentidad]['aportess'] += data.valor
                    
        # Convertir el diccionario acumulado en una lista de diccionarios
        compects = list(acumulados.values())
    
    # if request.method == 'POST':
    #     nomina_id = request.POST.get('nomina_select')
        
        
    # No need for else here, compects will be an empty list if it's not a POST request
    
    return render(request, 'companies/payrollsheet.html', {
        'nominas': nominas,
        'compects': compects,
        'selected_nomina':selected_nomina,
    })
