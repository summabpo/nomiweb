from django.shortcuts import render
from apps.companies.models import Nomina
import random
from datetime import datetime, timedelta

def payrollsheet(request):
    nominas = Nomina.objects.select_related('idnomina').values_list('idnomina__nombrenomina', 'idnomina').distinct().order_by('-idnomina')
    compects = []  # Define compects here

    if request.method == 'POST':
        nomina_id = request.POST.get('nomina_select')
        compectos = Nomina.objects.filter(idnomina = nomina_id )
        
        
        
        for data in compectos:
            
            compects.append({
                'documento': data.idempleado.docidentidad,
                'nombre': f"{data.idempleado.papellido} {data.idempleado.sapellido} {data.idempleado.pnombre} {data.idempleado.snombre}",
                'basico': data.valor ,
                'cargo': 'prueba',
                'centrocostos': 'prueba',
                'tipocontrato': 'prueba',
                'tarifaARL': 'prueba'
            })
        
    # No need for else here, compects will be an empty list if it's not a POST request
    
    return render(request, 'companies/payrollsheet.html', {
        'nominas': nominas,
        'compects': compects,
    })
