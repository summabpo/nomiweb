from django.shortcuts import render
from apps.companies.models import Nomina
from apps.components.humani import format_value

def payrollsheet(request):
    nominas = Nomina.objects.select_related('idnomina').values('idnomina__nombrenomina', 'idnomina').distinct().order_by('-idnomina')
    compects = []
    acumulados = {}

    selected_nomina = request.GET.get('nomina')
    if selected_nomina:
        compectos = Nomina.objects.filter(idnomina=selected_nomina)
        
        # Consulta 1: Total neto
        # neto = Nomina.objects.filter(idnomina=id_nomina).aggregate(Sum('valor'))['valor__sum'] or 0
        # # Consulta 2: Total ingresos
        # ingresos = Nomina.objects.filter(idnomina=id_nomina, valor__gt=0).aggregate(Sum('valor'))['valor__sum'] or 0
        # descuentos = neto - ingresos
        # # Consulta 3: Salario básico
        # basico = Nomina.objects.filter(idnomina=id_nomina, idconcepto__in=[1, 4]).aggregate(Sum('valor'))['valor__sum'] or 0
        # # Consulta 4: Transporte
        # transporte = Nomina.objects.filter(idnomina=id_nomina, idconcepto=2).aggregate(Sum('valor'))['valor__sum'] or 0
        # # Consulta 5: Extras
        # extras = Nomina.objects.filter(idnomina=id_nomina, conceptosdenomina__extras=1).aggregate(Sum('valor'))['valor__sum'] or 0
        # otrosing = ingresos - basico - extras - transporte
        # # Consulta 6: Aportes
        # aportes = Nomina.objects.filter(idnomina=id_nomina, conceptosdenomina__aportess=1).aggregate(Sum('valor'))['valor__sum'] or 0
        # # Consulta 7: Préstamos
        # prestamos = Nomina.objects.filter(idnomina=id_nomina, idconcepto=50).aggregate(Sum('valor'))['valor__sum'] or 0
        # otrosdesc = descuentos - prestamos - aportes
        # # Consulta 8: Estado email
        # estado_email = CrearNomina.objects.filter(idnomina=id_nomina).values_list('envio_email', flat=True).first()
        
        
        for data in compectos:
            docidentidad = data.idempleado.docidentidad
            
            if docidentidad not in acumulados:
                acumulados[docidentidad] = {
                    'documento': docidentidad,
                    'nombre': f"{data.idempleado.papellido} {data.idempleado.sapellido} {data.idempleado.pnombre} {data.idempleado.snombre}",
                    'neto': 0,
                    'ingresos': 0,
                    'basico': 0,
                    'tpte': 0,
                    'extras': 0,
                    'aportess': 0,
                    'prestamos': 0,
                }
            
            acumulados[docidentidad]['neto'] += data.valor
            acumulados[docidentidad]['ingresos'] += data.valor if data.valor > 0 else 0
            acumulados[docidentidad]['basico'] += data.valor if data.idconcepto.sueldobasico == 1 else 0
            acumulados[docidentidad]['tpte'] += data.valor if data.idconcepto.auxtransporte == 1 else 0
            acumulados[docidentidad]['extras'] += data.valor if data.idconcepto.extras == 1 else 0
            acumulados[docidentidad]['aportess'] += data.valor if data.idconcepto.aportess == 1 else 0
            acumulados[docidentidad]['prestamos'] += data.valor if data.idconcepto.idconcepto == 50 else 0
        
        compects = list(acumulados.values())

    for compect in compects:
        compect['descuentos'] = compect['neto'] - compect['ingresos']
        compect['otrosing'] = compect['ingresos'] - compect['basico'] - compect['extras'] - compect['tpte']
        compect['otrosdesc'] = compect['descuentos'] - compect['prestamos'] - compect['aportess']
        
        # Formatear los valores
        for key in ['neto', 'ingresos', 'basico', 'tpte', 'extras', 'aportess', 'prestamos', 'descuentos', 'otrosing', 'otrosdesc']:
            compect[key] = format_value(compect[key])

    return render(request, 'companies/payrollsheet.html', {
        'nominas': nominas,
        'compects': compects,
        'selected_nomina': selected_nomina,
    })
