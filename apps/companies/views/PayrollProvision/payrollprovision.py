

from django.shortcuts import render, redirect
from django.db import models
from django.db.models import Q, Sum
from django.contrib import messages
from apps.components.filterform import FilterForm  ,FiltercompleteForm
from apps.companies.models import  Nomina, Contratos, Conceptosfijos , Salariominimoanual
from datetime import datetime
from .provisionFuncion import calcular_descuento , mes_a_numero
from apps.components.humani import format_value
from django.http import HttpResponse 
from apps.components.generate_nomina_excel import generate_nomina_excel




def payrollprovision(request):
    acumulados = {}
    compects = []
    form = FiltercompleteForm()

    if request.method == 'POST':
        visual = True
        form = FiltercompleteForm(request.POST)
        if form.is_valid():
            año = form.cleaned_data['año']
            mes = form.cleaned_data['mes']
            
            year = año
            mth = mes
            
            # Obtener las nóminas filtradas y limitadas
            nominas = Nomina.objects.filter(mesacumular=mes, anoacumular=año).order_by('idempleado__papellido')
            
            # Obtener los conceptos fijos y almacenarlos en un diccionario
            conceptos_fijos = Conceptosfijos.objects.values('idfijo', 'valorfijo')
            conceptos_dict = {cf['idfijo']: cf['valorfijo'] for cf in conceptos_fijos}

            # Obtener los contratos y almacenarlos en un diccionario
            contratos = Contratos.objects.filter(idcontrato__in=nominas.values_list('idcontrato', flat=True))
            contratos_dict = {c.idcontrato: c for c in contratos}
            
            for data in nominas:
                docidentidad = data.idcontrato.idcontrato

                if docidentidad not in acumulados:
                    # Calcular la base para las prestaciones sociales
                    base_prestacion_social = Q(idconcepto__baseprestacionsocial=1)
                    sueldo_basico = Q(idconcepto__sueldobasico=1)

                    
                    
                    base = Nomina.objects.filter(
                        (base_prestacion_social | sueldo_basico),
                        mesacumular=mes,
                        anoacumular=año,
                        idcontrato=docidentidad
                    ).aggregate(total=Sum('valor'))['total'] or 0

                    contrato = contratos_dict.get(docidentidad)
                    tiposal = contrato.tiposalario if contrato else None
                    basico = contrato.salario if contrato else 0

                    # Obtener los valores de conceptos fijos
                    pces = conceptos_dict.get(7, 0)
                    ppri = conceptos_dict.get(6, 0)
                    pint = conceptos_dict.get(8, 0)
                    pvac = conceptos_dict.get(9, 0)

                    # Calcular prestaciones sociales
                    vacaciones = basico * pvac / 100
                    
                    if tiposal != 2:  # Si el tipo de salario no es integral
                        cesantias = base * pces / 100
                        intcesa = base * pint / 100
                        prima = base * ppri / 100
                    else:
                        cesantias = intcesa = prima = 0

                    total_ps = cesantias + intcesa + prima + vacaciones

                    # Agregar los cálculos al diccionario
                    acumulados[docidentidad] = {
                        'documento': data.idempleado.docidentidad,
                        'nombre': f"{data.idempleado.papellido} {data.idempleado.sapellido} {data.idempleado.pnombre} {data.idempleado.snombre}",
                        'contrato': data.idcontrato.idcontrato,
                        'idcosto': data.idcosto.idcosto,
                        'base': format_value (int(base)),
                        'cesantias': format_value (int(cesantias)),
                        'intcesa': format_value (int(intcesa)),
                        'prima': format_value (int(prima)),
                        'vacaciones': format_value (int(vacaciones)),
                        'total_ps': format_value (int(total_ps)),
                    }
            compects = list(acumulados.values())
    else :
        visual = False
        year = 0
        mth = 0


        
        
    return render(request, 'companies/payrollprovision.html', {
        'form': form,
        'visual':visual,
        'year' : year,
        'mth' : mth,
        'compects': compects
    })
    
def payrollprovisiondownload_excel(request):
    year = request.GET.get('year')
    mth = request.GET.get('mth')

    # Verificar si year y mth están presentes
    if not year or not mth:
        return HttpResponse("Faltan parámetros.", status=400)

    # Generar el archivo Excel
    excel_data = generate_nomina_excel(year, mth)

    # Crear la respuesta con el archivo Excel
    response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="provisionalidades.xlsx"'
    
    return response
    

def contributionsprovision(request):
    acumulados = {}
    compects = []
    form = FilterForm()

    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            año = form.cleaned_data['año']
            mes = form.cleaned_data['mes']
            
            # Obtener las nóminas filtradas y limitadas
            nominas = Nomina.objects.filter(mesacumular=mes, anoacumular=año).order_by('idempleado__papellido')
            
            # Obtener los conceptos fijos y almacenarlos en un diccionario
            conceptos_fijos = Conceptosfijos.objects.values('idfijo', 'valorfijo')
            conceptos_dict = {cf['idfijo']: cf['valorfijo'] for cf in conceptos_fijos}

            for data in nominas:
                docidentidad = data.idcontrato.idcontrato
                fechainicial = datetime.strptime(f"{año}-{mes_a_numero(mes)}-01", "%Y-%m-%d").date()
                fechafinal = datetime.strptime(f"{año}-{mes_a_numero(mes)}-30", "%Y-%m-%d").date()         

                if docidentidad not in acumulados:
                    
                    contrato = Contratos.objects.filter(idcontrato=docidentidad).first()

                    if contrato:
                        fechacontrato = contrato.fechainiciocontrato
                        fechaterminacion = contrato.fechafincontrato

                        if fechacontrato <= fechainicial:
                            diasaportes = 30
                        else:
                            diasaportes = (fechafinal - fechacontrato).days + 1

                        if fechaterminacion:
                            if fechaterminacion >= fechainicial and fechaterminacion <= fechafinal:
                                resto = (fechafinal - fechaterminacion).days
                                diasaportes -= resto
                    else:
                        diasaportes = 0
                    
                    
                    
                    # Crear un diccionario con los filtros para cada tipo de base
                    filters = {
                        'base_ss': Q(idconcepto__basesegsocial=1),
                        'base_arl': Q(idconcepto__baserarl=1),
                        'base_caja': Q(idconcepto__basecaja=1),
                        'pension_t': Q(idconcepto__idconcepto=70),
                        'pension_ft': Q(idconcepto__idconcepto=90),
                        'salud_t': Q(idconcepto__idconcepto=60),
                        'variable': Q(idconcepto__sueldobasico=1) | Q(idconcepto__salintegral=1) | Q(idconcepto__incapacidad=1) | Q(idconcepto__idconcepto=24),
                        'suspension': Q(idconcepto__suspcontrato=1),
                    }

                    # Inicializar un diccionario para almacenar los resultados
                    results = {}

                    # Ejecutar una consulta para cada filtro
                    for key, filter_criteria in filters.items():
                        result = Nomina.objects.filter(
                            filter_criteria,
                            mesacumular=mes,
                            anoacumular=año,
                            idcontrato=docidentidad
                        ).aggregate(total=Sum('valor'))
                        results[key] = result['total'] or 0

                    # Extraer los resultados del diccionario
                    base_ss = results['base_ss']
                    base_arl = results['base_arl']
                    base_caja = results['base_caja']
                    pension_t = results['pension_t']
                    pension_ft = results['pension_ft']
                    salud_t = results['salud_t']
                    variable = base_ss - results['variable']
                    suspension = results['suspension']
                    
                    
                    
                    # Determinar porcentaje de ARL y tipo de salario por empleado
                    contrato = Contratos.objects.filter(idcontrato=docidentidad).values(
                        'tarifaarl', 'tiposalario', 'eps', 'pension', 'cajacompensacion', 'tipocontrato'
                    ).first()

                    if contrato:
                        tararl = contrato['tarifaarl']
                        tiposal = contrato['tiposalario']
                        afp = contrato['pension']
                        eps = contrato['eps']
                        caja = contrato['cajacompensacion']
                        tipocontrato = contrato['tipocontrato']
                    else:
                        tararl = tiposal = afp = eps = caja = tipocontrato = 0

                    
                
                    ppene = conceptos_dict.get(13, 0)
                    psalude = conceptos_dict.get(20, 0)
                    pccf = conceptos_dict.get(21, 0)
                    psena = conceptos_dict.get(22, 0)
                    picbf = conceptos_dict.get(23, 0)
                    nummin = conceptos_dict.get(24, 0)
                    maxibc = conceptos_dict.get(4, 0)
                    facint = conceptos_dict.get(3, 0)
                    pepse = conceptos_dict.get(10, 0)
                    ppenem = conceptos_dict.get(12, 0)
                    
                    
                    
                    
                    try:
                        salmin = Salariominimoanual.objects.get(idano=año).salariominimo
                    except Salariominimoanual.DoesNotExist:
                        salmin = None  

                    if tiposal == 2:
                        base_ss *= facint / 100
                        base_caja = base_ss
                        base_arl = base_ss

                    if base_ss > (salmin * maxibc):
                        base_ss = salmin * maxibc
                        base_caja = base_ss
                        base_arl = base_ss
                        
                    if base_ss > (salmin * maxibc):
                        base_ss = salmin * maxibc
                        base_caja = base_ss
                        base_arl = base_ss
                    
                

                    if base_ss <= (salmin * nummin):
                        salud = 0
                        pension = ((base_ss + suspension) * ppene / 100) + (suspension * ppenem / 100)
                        arl = float(base_arl) * float(tararl) / 100
                        ccf = base_caja * pccf / 100
                        sena = 0
                        icbf = 0
                    else:
                        salud = (base_ss + suspension) * psalude / 100
                        pension = ((base_ss + suspension) * ppene / 100) + (suspension * ppenem / 100)
                        arl = base_arl * tararl / 100
                        ccf = base_caja * pccf / 100
                        sena = base_ss * psena / 100
                        icbf = base_ss * picbf / 100

                    if tiposal == 2:
                        salud = base_ss * psalude / 100
                        pension = ((base_ss + suspension) * ppene / 100) + (suspension * ppenem / 100)
                        arl = base_arl * tararl / 100
                        ccf = base_caja * pccf / 100
                        sena = base_ss * psena / 100
                        icbf = base_ss * picbf / 100

                    if (base_ss / diasaportes * 30) < salmin and base_ss > 0:
                        base_ss = salmin
                        ajuste = (((base_ss * pepse / 100) + salud_t) + ((base_ss * ppenem / 100) + pension_t))
                        pension = ((base_ss + suspension) * ppene / 100) + (suspension * ppenem / 100)
                        base_arl = base_ss
                        base_caja = base_ss
                        arl = base_arl * tararl / 100
                        ccf = base_caja * pccf / 100
                        sena = 0
                        icbf = 0
                        variable = 0
                    else:
                        ajuste = 0

                    if tipocontrato == 5:
                        salud = salmin * (psalude / 100 + pepse / 100)

                    totalap = float(salud) + float(pension) + float(arl) + float(ccf) + float(sena) + float(icbf) - float(salud_t) - float(pension_t) - float(pension_ft) + float(ajuste)

                    provision = totalap + salud_t + pension_t
                    
                    fsp = calcular_descuento(base_ss,salmin)
                    
                    # Agregar los cálculos al diccionario
                    acumulados[docidentidad] = {
                        'documento': data.idempleado.docidentidad,
                        'nombre': f"{data.idempleado.papellido} {data.idempleado.sapellido} {data.idempleado.pnombre} {data.idempleado.snombre}",
                        'contrato': data.idcontrato.idcontrato,
                        'idcosto': data.idcosto.idcosto,
                        'diasaportes': diasaportes,
                        'base_ss': base_ss,
                        'base_arl': base_arl,
                        'base_caja': base_caja,
                        'pension_t': pension_t,
                        'pension_ft': pension_ft,
                        'salud_t': salud_t,
                        'variable': variable,
                        'suspension': suspension,
                        'salud': salud,
                        'pension': pension,
                        'arl': arl,
                        'ccf': ccf,
                        'sena': sena,
                        'icbf': icbf,
                        'ajuste': ajuste,
                        'totalap': totalap,
                        'provision': provision,
                        'fsp' : fsp ,
                        'afp' : afp ,
                        'eps' : eps,
                        'caja' : caja,
                        
                
                    }
                else:
                    # Actualiza la base si ya existe
                    acumulados[docidentidad]['base'] = data.valor if data.idconcepto.sueldobasico == 1 else acumulados[docidentidad].get('base', 0)

            compects = list(acumulados.values())

    return render(request, 'companies/contributionsprovision.html', {
        'form': form,
        'compects': compects
    })
    
