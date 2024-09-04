

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
                        'cesantias': cesantias,
                        'intcesa': intcesa,
                        'prima': prima,
                        'vacaciones': vacaciones,
                        'total_ps': total_ps
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
    
    
""" 
def calcular_provision_prestaciones_sociales(contrato_id, mes_acumular, ano_acumular):
    # Calculo de la base para las prestaciones sociales
    # Se suman los valores de nómina que corresponden a conceptos
    # con base prestacional o sueldo básico para el contrato, mes y año específicos.
    base = Nomina.objects.filter(
        models.Q(conceptosdenomina__baseprestacionsocial=1) |
        models.Q(conceptosdenomina__sueldobasico=1),
        mesacumular=mes_acumular,
        anoacumular=ano_acumular,
        idcontrato=contrato_id
    ).aggregate(total=models.Sum('valor'))['total'] or 0

    # Obtiene datos del contrato: porcentaje de ARL y tipo de salario
    # Se obtiene el tipo de salario y el salario básico del contrato específico.
    contrato = Contrato.objects.filter(idcontrato=contrato_id).first()
    tiposal = contrato.tiposalario if contrato else None
    basico = contrato.salario if contrato else 0

    # Obtiene los porcentajes fijos
    # Se consultan todos los conceptos fijos, que incluyen porcentajes y valores
    # que se utilizarán para calcular las prestaciones.
    conceptos_fijos = Conceptosfijos.objects.order_by('idfijo').all()

    # Inicialización de variables para los diferentes porcentajes fijos.
    pces, ppri, pint, pvac, ppene, psalude, pccf, psena, picbf, nummin, maxibc, facint = [0]*12

    # Asignación de valores a cada porcentaje fijo según su ID en la base de datos.
    for concepto in conceptos_fijos:
        if concepto.idfijo == 7:
            pces = concepto.valorfijo
        elif concepto.idfijo == 6:
            ppri = concepto.valorfijo
        elif concepto.idfijo == 8:
            pint = concepto.valorfijo
        elif concepto.idfijo == 9:
            pvac = concepto.valorfijo
        elif concepto.idfijo == 13:
            ppene = concepto.valorfijo
        elif concepto.idfijo == 20:
            psalude = concepto.valorfijo
        elif concepto.idfijo == 21:
            pccf = concepto.valorfijo
        elif concepto.idfijo == 22:
            psena = concepto.valorfijo
        elif concepto.idfijo == 23:
            picbf = concepto.valorfijo
        elif concepto.idfijo == 24:
            nummin = concepto.valorfijo
        elif concepto.idfijo == 4:
            maxibc = concepto.valorfijo
        elif concepto.idfijo == 3:
            facint = concepto.valorfijo

    # Calculo de prestaciones sociales
    # Se inicializan las prestaciones con valores base.
    cesantias = 0
    intcesa = 0
    prima = 0
    vacaciones = basico * pvac / 100

    # Si el tipo de salario no es 2 (salario integral),
    # se calculan las prestaciones sociales como cesantías, intereses sobre cesantías, y prima.
    if tiposal != 2:
        cesantias = base * pces / 100
        intcesa = base * pint / 100
        prima = base * ppri / 100

    # Se calcula el total de las prestaciones sociales sumando todos los conceptos calculados.
    total_ps = cesantias + intcesa + prima + vacaciones
    
    # Retorna un diccionario con los resultados de las prestaciones calculadas.
    return {
        'base_ps': base,          # Base para prestaciones sociales
        'cesantias': cesantias,   # Monto de cesantías
        'intcesa': intcesa,       # Intereses sobre cesantías
        'prima': prima,           # Prima de servicios
        'vacaciones': vacaciones, # Monto para vacaciones
        'total_ps': total_ps,     # Total de prestaciones sociales
    }

"""

