

from django.shortcuts import render, redirect
from django.db import models
from django.db.models import Q, Sum
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.companies.models import  Nomina, Contratos, Conceptosfijos


def payrollprovision(request):
    acumulados = {}
    compects = []
    form = FilterForm()

    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            año = form.cleaned_data['año']
            mes = form.cleaned_data['mes']
            
            # Obtener las nóminas filtradas y limitadas
            nominas = Nomina.objects.filter(mesacumular=mes, anoacumular=año).order_by('idempleado__papellido')[:100]
            
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
                    # ppene = conceptos_dict.get(13, 0)
                    # psalude = conceptos_dict.get(20, 0)
                    # pccf = conceptos_dict.get(21, 0)
                    # psena = conceptos_dict.get(22, 0)
                    # picbf = conceptos_dict.get(23, 0)
                    # nummin = conceptos_dict.get(24, 0)
                    # maxibc = conceptos_dict.get(4, 0)
                    # facint = conceptos_dict.get(3, 0)

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
                        'base': data.valor if data.idconcepto.sueldobasico == 1 else 0,
                        'cesantias': int(cesantias),
                        'intcesa': int(intcesa),
                        'prima': int(prima),
                        'vacaciones': int(vacaciones),
                        'total_ps': int(total_ps)
                    }
                else:
                    # Actualiza la base si ya existe
                    acumulados[docidentidad]['base'] = data.valor if data.idconcepto.sueldobasico == 1 else acumulados[docidentidad].get('base', 0)

            compects = list(acumulados.values())

    return render(request, 'companies/payrollprovision.html', {
        'form': form,
        'compects': compects
    })
    
    
    
    

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
            nominas = Nomina.objects.filter(mesacumular=mes, anoacumular=año).order_by('idempleado__papellido')[:100]
            
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
                    # ppene = conceptos_dict.get(13, 0)
                    # psalude = conceptos_dict.get(20, 0)
                    # pccf = conceptos_dict.get(21, 0)
                    # psena = conceptos_dict.get(22, 0)
                    # picbf = conceptos_dict.get(23, 0)
                    # nummin = conceptos_dict.get(24, 0)
                    # maxibc = conceptos_dict.get(4, 0)
                    # facint = conceptos_dict.get(3, 0)

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
                        'base': data.valor if data.idconcepto.sueldobasico == 1 else 0,
                        # 'cesantias': cesantias,
                        # 'intcesa': intcesa,
                        # 'prima': prima,
                        # 'vacaciones': vacaciones,
                        # 'total_ps': total_ps
                    }
                else:
                    # Actualiza la base si ya existe
                    acumulados[docidentidad]['base'] = data.valor if data.idconcepto.sueldobasico == 1 else acumulados[docidentidad].get('base', 0)

            compects = list(acumulados.values())

    return render(request, 'companies/contributionsprovision.html', {
        'form': form,
        'compects': compects
    })
    

def calcular_provision(request, idcontrato, mesacumular, anoacumular):
    # Calcular los días a liquidar en la nómina
    idmes = mesacumular.zfill(2)  # Asegura que el mes tenga dos dígitos
    fechainicial = f"{anoacumular}-{idmes}-01"
    fechafinal = f"{anoacumular}-{idmes}-30"

    contrato = Contratos.objects.filter(idcontrato=idcontrato).first()

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

    # Calcular valores de seguridad social
    base_ss = AportesSS.objects.filter(
        basesegsocial=1, mesacumular=mesacumular, anoacumular=anoacumular, idcontrato=idcontrato
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    base_arl = AportesSS.objects.filter(
        baserarl=1, mesacumular=mesacumular, anoacumular=anoacumular, idcontrato=idcontrato
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    base_caja = AportesSS.objects.filter(
        basecaja=1, mesacumular=mesacumular, anoacumular=anoacumular, idcontrato=idcontrato
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    pension_t = AportesSS.objects.filter(
        idconcepto=70, mesacumular=mesacumular, anoacumular=anoacumular, idcontrato=idcontrato
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    pension_ft = AportesSS.objects.filter(
        idconcepto=90, mesacumular=mesacumular, anoacumular=anoacumular, idcontrato=idcontrato
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    salud_t = AportesSS.objects.filter(
        idconcepto=60, mesacumular=mesacumular, anoacumular=anoacumular, idcontrato=idcontrato
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    variable = base_ss - AportesSS.objects.filter(
        mesacumular=mesacumular, anoacumular=anoacumular, idcontrato=idcontrato
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    suspension = AportesSS.objects.filter(
        suspcontrato=1, mesacumular=mesacumular, anoacumular=anoacumular, idcontrato=idcontrato
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    # Determinar porcentaje de ARL y tipo de salario por empleado
    contrato = Contratos.objects.filter(idcontrato=idcontrato).values(
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

    # Porcentajes fijos
    conceptos_fijos = ConceptosFijos.objects.all()
    fixed_values = {cf.conceptofijo: cf.valorfijo for cf in conceptos_fijos}

    ppene = fixed_values.get(13, 0)
    psalude = fixed_values.get(20, 0)
    pccf = fixed_values.get(21, 0)
    psena = fixed_values.get(22, 0)
    picbf = fixed_values.get(23, 0)
    nummin = fixed_values.get(24, 0)
    maxibc = fixed_values.get(4, 0)
    facint = fixed_values.get(3, 0)
    pepse = fixed_values.get(10, 0)
    ppenem = fixed_values.get(12, 0)

    salmin = 1000  # Define el salario mínimo según tus necesidades

    if tiposal == 2:
        base_ss *= facint / 100
        base_caja = base_ss
        base_arl = base_ss

    if base_ss > (salmin * maxibc):
        base_ss = salmin * maxibc
        base_caja = base_ss
        base_arl = base_ss

    if base_ss <= (salmin * nummin):
        salud = 0
        pension = ((base_ss + suspension) * ppene / 100) + (suspension * ppenem / 100)
        arl = base_arl * tararl / 100
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

    totalap = salud + pension + arl + ccf + sena + icbf - salud_t - pension_t - pension_ft + ajuste
    provision = totalap + salud_t + pension_t

    context = {
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
    }

    return render(request, 'path/to/your/template.html', context)


