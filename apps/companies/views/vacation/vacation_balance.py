from django.shortcuts import render
from apps.companies.models import Contratosemp , Vacaciones ,Contratos 
from django.db.models import Q, Sum


def vacation_balance(request):
    acumulados = {}
    
    contratos_empleados = Contratos.objects\
        .select_related('idempleado') \
        .filter(estadocontrato=1) \
        .values('idempleado__docidentidad', 'idempleado__sapellido', 'idempleado__papellido', 
                'idempleado__pnombre', 'idempleado__snombre', 'idempleado__idempleado', 
                'idcontrato', 'fechainiciocontrato') 
        
        
    
    for data in contratos_empleados:
        docidentidad = data['idcontrato']
        
        # base = Vacaciones.objects.filter(
        #                     idcontrato=docidentidad
        #                 ).aggregate(total=Sum('valor'))['total'] or 0
        
        if docidentidad not in acumulados:
            acumulados[docidentidad] = {
                'contrato': data['idcontrato'],
                'documento': data['idempleado__docidentidad'],
                'empleado': f"{data['idempleado__papellido']} {data['idempleado__sapellido']} {data['idempleado__pnombre']} {data['idempleado__snombre']}",
                'fechacontrato': data['fechainiciocontrato'],
            }
    
    compects = list(acumulados.values())
    context = {
        'contratos_empleados': compects,
    }
    
    return render(request, './companies/vacation_balance.html', context)