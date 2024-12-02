

from django.shortcuts import render, redirect
from django.db import models
from django.db.models import Q, Sum, DecimalField, F
from django.contrib import messages
from apps.components.filterform import FilterForm  ,FiltercompleteForm
from apps.common.models  import  Nomina, Contratos, Conceptosfijos , Salariominimoanual ,NominaComprobantes
from datetime import datetime
from .provisionFuncion import calcular_descuento , mes_a_numero ,mes_a_numero2
from apps.components.humani import format_value
from django.http import HttpResponse 
from apps.components.generate_nomina_excel import generate_nomina_excel

from decimal import Decimal
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from io import BytesIO

# Función para verificar si un año es bisiesto
def es_bisiesto(año):
    año = int(año)
    return año % 4 == 0 and (año % 100 != 0 or año % 400 == 0)

# Función para obtener el último día del mes
def ultimo_dia_del_mes(año, mes):
    if mes == 2:  # Febrero
        if es_bisiesto(año):
            return 29
        else:
            return 28
    elif mes in [4, 6, 9, 11]:  # Abril, Junio, Septiembre, Noviembre
        return 30
    else:
        return 31


def payrollprovision(request):
    acumulados = {}
    compects = []
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = FiltercompleteForm()

    if request.method == 'POST':
        visual = True
        form = FiltercompleteForm(request.POST)
        if form.is_valid():
            año = form.cleaned_data['año']
            mes = form.cleaned_data['mes']
            dta = form.cleaned_data['liquidation']
            
            year = año
            mth = mes
            
            # Obtener las nóminas filtradas con `select_related` para optimizar la carga de datos relacionados
            nominas = Nomina.objects.filter(idnomina__mesacumular=mes, idnomina__anoacumular__ano=año,idnomina__id_empresa__idempresa = idempresa).select_related('idcontrato', 'idcosto').order_by('idcontrato__idempleado__papellido')

            # Obtener los conceptos fijos y almacenarlos en un diccionario fuera del bucle
            conceptos_fijos = Conceptosfijos.objects.values('idfijo', 'valorfijo')
            conceptos_dict = {cf['idfijo']: cf['valorfijo'] for cf in conceptos_fijos}

            # Obtener los contratos relevantes de una sola vez
            contratos_dict = {
                contrato.idcontrato: contrato 
                for contrato in Contratos.objects.filter(idcontrato__in=nominas.values_list('idcontrato', flat=True))
            }

            # Calcular la base para prestaciones sociales y sueldo básico fuera del bucle
            base_prestacion_social = Q(idconcepto__baseprestacionsocial=1)
            sueldo_basico = Q(idconcepto__sueldobasico=1)
            aux_transporte = Q(idconcepto__auxtransporte=1)

            for data in nominas:
                docidentidad = data.idcontrato.idcontrato
                if docidentidad not in acumulados:
                    # Condición para calcular base dependiendo de 'dta'
                    
                    if dta == '1':
                        
                        base = Nomina.objects.filter(
                            (base_prestacion_social | sueldo_basico | aux_transporte ),
                            idnomina__mesacumular=mes,
                            idnomina__anoacumular__ano=año,
                            idcontrato=docidentidad
                        ).aggregate(total=Sum('valor'))['total'] or 0
                        
                        base_vacaciones = NominaComprobantes.objects.filter(
                            idcontrato=docidentidad,
                        ).values_list('salario', flat=True).order_by('-idhistorico').first() or 0
                    
                    else:
                        base = base_vacaciones = NominaComprobantes.objects.filter(
                            idcontrato=docidentidad,
                        ).values_list('salario', flat=True).order_by('-idhistorico').first() or 0
                    
                    
                    
                    contrato = contratos_dict.get(docidentidad)
                    tiposal = contrato.tiposalario if contrato else None

                    # Obtener los valores de conceptos fijos
                    pces = conceptos_dict.get(7, 0)
                    ppri = conceptos_dict.get(6, 0)
                    pint = conceptos_dict.get(8, 0)
                    pvac = conceptos_dict.get(9, 0)

                    # Calcular prestaciones sociales
                    vacaciones = base_vacaciones * pvac / 100
                    cesantias = float(base) * float(pces) / 100
                    intcesa = base * pint / 100
                    prima = base * ppri / 100
                    
                    if tiposal.idtiposalario == 2: 
                        cesantias = 0
                        intcesa = 0
                        prima = 0
                    
                    if data.idcontrato.tipocontrato.idtipocontrato not in [1, 2, 3, 4]: 
                        cesantias = intcesa = prima = vacaciones = 0

                    # Convertir a Decimal si no lo son
                    cesantias = Decimal(cesantias)
                    intcesa = Decimal(intcesa)
                    prima = Decimal(prima)
                    vacaciones = Decimal(vacaciones)

                    total_ps = cesantias + intcesa + prima + vacaciones

                    # Agregar los cálculos al diccionario
                    acumulados[docidentidad] = {
                        'documento': data.idcontrato.idempleado.docidentidad,
                        'nombre': f"{data.idcontrato.idempleado.papellido} {data.idcontrato.idempleado.sapellido} {data.idcontrato.idempleado.pnombre} {data.idcontrato.idempleado.snombre}",
                        'contrato': data.idcontrato.idcontrato,
                        'idcosto': data.idcosto.idcosto,
                        'base': format_value(int(base)),
                        'cesantias': format_value(int(cesantias)),
                        'intcesa': format_value(int(intcesa)),
                        'prima': format_value(int(prima)),
                        'vacaciones': format_value(int(vacaciones)),
                        'total_ps': format_value(int(total_ps)),
                    }

            # Convertir acumulados en una lista de resultados
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
    """
    Handles the download of payroll provision data as an Excel file.
    """
    """
    Handles the download of payroll provision data as an Excel file.
    """
    year = request.GET.get('year')
    mth = request.GET.get('mth')
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    # Verificar si year y mth están presentes
    if not year or not mth:
        return HttpResponse("Faltan parámetros.", status=400)

    # Generar el archivo Excel
    excel_data = generate_nomina_excel(year, mth,idempresa)

    # Crear la respuesta con el archivo Excel
    response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="provisionalidades.xlsx"'
    
    return response


def contributionsprovision(request):
    acumulados = {}
    compects = []
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = FilterForm()

    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            año = form.cleaned_data['año']
            mes = form.cleaned_data['mes']
            
            year = año
            mth = mes
            
            # Obtener las nóminas filtradas y limitadas
            nominas = Nomina.objects.filter(idnomina__mesacumular=mes, idnomina__anoacumular__ano=año,idnomina__id_empresa__idempresa = idempresa).order_by('idcontrato__idempleado__papellido')
            
            print('--------------------')
            print(f'Número de registros: {nominas.count()}')
            print('--------------------')
            
            # Obtener los conceptos fijos y almacenarlos en un diccionario
            conceptos_fijos = Conceptosfijos.objects.values('idfijo', 'valorfijo')
            conceptos_dict = {cf['idfijo']: cf['valorfijo'] for cf in conceptos_fijos}

            for data in nominas:
                docidentidad = data.idcontrato.idcontrato
                
                # Convierte el mes a número
                mes_numero = mes_a_numero2(mes)  # Asegúrate de que esta función devuelve el número correcto del mes.
                ultimo_dia = ultimo_dia_del_mes(año, mes_numero)
                # Formar la fecha inicial y final
                fechainicial = datetime.strptime(f"{año}-{mes_numero}-01", "%Y-%m-%d").date()
                fechafinal = datetime.strptime(f"{año}-{mes_numero}-{ultimo_dia}", "%Y-%m-%d").date()     


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
                            idnomina__mesacumular=mes,
                            idnomina__anoacumular__ano=año,
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
                    variable = base_ss - results['variable'] ## base_ss - suel;do vaci
                    suspension = results['suspension']
                    # bss concepto base secsocual
                    
                    
                    # Determinar porcentaje de ARL y tipo de salario por empleado
                    contrato = Contratos.objects.filter(idcontrato=docidentidad).values(
                        'centrotrabajo__tarifaarl', 'tiposalario', 'codeps__entidad', 'codafp__entidad', 'codccf__entidad', 'tipocontrato__tipocontrato'
                    ).first()
                    
                    
                    
                    salario = NominaComprobantes.objects.filter(
                            idcontrato = docidentidad,
                            idnomina = data.idnomina.idnomina
                        ).values_list('salario', flat=True).order_by('-idhistorico').first() or 0

                    if contrato:
                        tararl = contrato['centrotrabajo__tarifaarl']
                        tiposal = contrato['tiposalario']
                        afp = contrato['codafp__entidad']
                        eps = contrato['codeps__entidad']
                        caja = contrato['codccf__entidad']
                        tipocontrato = contrato['tipocontrato__tipocontrato']
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
                        salmin = Salariominimoanual.objects.get(ano=año).salariominimo
                    except Salariominimoanual.DoesNotExist:
                        salmin = 0 

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
                        ccf = float(base_caja) * float(pccf) / 100
                        sena = 0
                        icbf = 0
                    else:
                        salud = (base_ss + suspension) * psalude / 100
                        pension = ((base_ss + suspension) * ppene / 100) + (suspension * ppenem / 100)
                        arl = float(base_arl) * float(tararl) / 100
                        ccf = float(base_caja) * float(pccf) / 100
                        sena = float(base_ss) * float(psena) / 100
                        icbf = float(base_ss) *float(picbf) / 100

                    if tiposal == 2:
                        salud = base_ss * psalude / 100
                        pension = ((base_ss + suspension) * ppene / 100) + (suspension * ppenem / 100)
                        arl = float(base_arl) * float (tararl) / 100
                        ccf = float(base_caja) * float(pccf) / 100
                        sena = float(base_ss) * float(psena) / 100
                        icbf = float(base_ss) * float(picbf) / 100

                    if (base_ss / diasaportes * 30) < salmin and base_ss > 0 :
                        ajuste = (((float(base_ss) * float(pepse) / 100) + float(salud_t)) + ((float(base_ss) * float(ppenem) / 100) + float(pension_t)))
                        pension = ((float(base_ss) + float(suspension)) * float(ppene) / 100) + (float(suspension) * float(ppenem) / 100)
                        base_arl = float(base_ss)
                        base_caja = float(base_ss)
                        arl = float(base_arl) * float(tararl) / 100
                        ccf = float(base_caja) * float(pccf) / 100
                        sena = 0
                        icbf = 0
                        variable = 0
                    else:
                        ajuste = 0

                    if tipocontrato == 5:
                        salud = salmin * (psalude / 100 + pepse / 100)

                    totalap = float(salud) + float(pension) + float(arl) + float(ccf) + float(sena) + float(icbf) - float(salud_t) - float(pension_t) - float(pension_ft) + float(ajuste)

                    provision = totalap + salud_t + pension_t
                    
                    fsp = calcular_descuento(int(base_ss),salmin)
                
                    acumulados[docidentidad] = {
                        'documento': data.idcontrato.idempleado.docidentidad,
                        'nombre': f"{data.idcontrato.idempleado.papellido} {data.idcontrato.idempleado.sapellido} {data.idcontrato.idempleado.pnombre} {data.idcontrato.idempleado.snombre}",
                        'contrato': data.idcontrato.idcontrato,
                        'idcosto': data.idcosto.idcosto,
                        'salario': format_value(int(salario)),
                        'diasaportes': format_value(int(diasaportes)) ,
                        'base_ss': format_value(int(base_ss)) ,
                        'base_arl': format_value(int(base_arl)) ,
                        'base_caja': format_value(int(base_caja)) ,
                        'pension_t': format_value(int(pension_t)) ,
                        'pension_ft': format_value(int(pension_ft)) ,
                        'salud_t': format_value(int(salud_t)) ,
                        'variable': format_value(int(variable)) ,
                        'suspension': format_value(int(suspension)) ,
                        'salud': format_value(int(salud)) ,
                        'pension': format_value(int(pension)) ,
                        'arl': format_value(int(arl)) ,
                        'ccf': format_value(int(ccf)) ,
                        'sena': format_value(int(sena)) ,
                        'icbf': format_value(int(icbf)) ,
                        'ajuste': format_value(int(ajuste)) ,
                        'totalap': format_value(int(totalap)) ,
                        'provision': format_value(int(provision)) ,
                        'fsp' : format_value(int(fsp)) ,
                        'afp' : afp  ,
                        'eps' : eps,
                        'caja' : caja,
                        
                
                    }

            compects = list(acumulados.values())

    else:
        year = 0
        mth = 0
    return render(request, 'companies/contributionsprovision.html', {
        'form': form,
        'year' : year,
        'mth' : mth,
        'compects': compects
    })

def contributionsprovisiondownload_excel(request):
    year = request.GET.get('year')
    mth = request.GET.get('mth')
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    # Verificar si year y mth están presentes
    if not year or not mth:
        return HttpResponse("Faltan parámetros.", status=400)

    # Generar el archivo Excel
    excel_data = generate_nomina_excel2(year, mth,idempresa)

    # Crear la respuesta con el archivo Excel
    response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="provisionalidades.xlsx'
    
    return response


def generate_nomina_excel2(year, mth, idempresa):
    acumulados = {}

    # Obtener los datos de la base de datos
    nominas = Nomina.objects.filter(
        idnomina__mesacumular=mth, idnomina__anoacumular__ano=year, idnomina__id_empresa__idempresa=idempresa
    ).order_by('idcontrato__idempleado__papellido')

    conceptos_fijos = Conceptosfijos.objects.values('idfijo', 'valorfijo')
    conceptos_dict = {cf['idfijo']: cf['valorfijo'] for cf in conceptos_fijos}

    # Rellenar el diccionario `acumulados` fuera del ciclo
    for data in nominas:
        docidentidad = data.idcontrato.idcontrato
        mes_numero = mes_a_numero2(mth)
        ultimo_dia = ultimo_dia_del_mes(year, mes_numero)
        fechainicial = datetime.strptime(f"{year}-{mes_numero}-01", "%Y-%m-%d").date()
        fechafinal = datetime.strptime(f"{year}-{mes_numero}-{ultimo_dia}", "%Y-%m-%d").date()

        contrato = Contratos.objects.filter(idcontrato=docidentidad).first()
        if contrato:
            fechacontrato = contrato.fechainiciocontrato
            fechaterminacion = contrato.fechafincontrato
            if fechacontrato <= fechainicial:
                diasaportes = 30
            else:
                diasaportes = (fechafinal - fechacontrato).days + 1
            if fechaterminacion and fechaterminacion >= fechainicial and fechaterminacion <= fechafinal:
                resto = (fechafinal - fechaterminacion).days
                diasaportes -= resto
        else:
            diasaportes = 0

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

        results = {}
        for key, filter_criteria in filters.items():
            result = Nomina.objects.filter(
                filter_criteria,
                idnomina__mesacumular=mth,
                idnomina__anoacumular__ano=year,
                idcontrato=docidentidad
            ).aggregate(total=Sum('valor'))
            results[key] = result['total'] or 0

        base_ss = results['base_ss']
        base_arl = results['base_arl']
        base_caja = results['base_caja']
        pension_t = results['pension_t']
        pension_ft = results['pension_ft']
        salud_t = results['salud_t']
        variable = base_ss - results['variable']
        suspension = results['suspension']

        contrato = Contratos.objects.filter(idcontrato=docidentidad).values(
            'centrotrabajo__tarifaarl', 'tiposalario', 'codeps__entidad', 'codafp__entidad', 'codccf__entidad', 'tipocontrato__tipocontrato'
        ).first()

        salario = NominaComprobantes.objects.filter(
            idcontrato=docidentidad,
            idnomina=data.idnomina.idnomina
        ).values_list('salario', flat=True).order_by('-idhistorico').first() or 0

        if contrato:
            tararl = contrato['centrotrabajo__tarifaarl']
            tiposal = contrato['tiposalario']
            afp = contrato['codafp__entidad']
            eps = contrato['codeps__entidad']
            caja = contrato['codccf__entidad']
            tipocontrato = contrato['tipocontrato__tipocontrato']
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
            salmin = Salariominimoanual.objects.get(ano=year).salariominimo
        except Salariominimoanual.DoesNotExist:
            salmin = 0

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
            arl = float(base_arl) * float(tararl) / 100
            ccf = float(base_caja) * float(pccf) / 100
            sena = 0
            icbf = 0
        else:
            salud = (base_ss + suspension) * psalude / 100
            pension = ((base_ss + suspension) * ppene / 100) + (suspension * ppenem / 100)
            arl = float(base_arl) * float(tararl) / 100
            ccf = float(base_caja) * float(pccf) / 100
            sena = float(base_ss) * float(psena) / 100
            icbf = float(base_ss) * float(picbf) / 100

        if tiposal == 2:
            salud = base_ss * psalude / 100
            pension = ((base_ss + suspension) * ppene / 100) + (suspension * ppenem / 100)
            arl = float(base_arl) * float(tararl) / 100
            ccf = float(base_caja) * float(pccf) / 100
            sena = float(base_ss) * float(psena) / 100
            icbf = float(base_ss) * float(picbf) / 100

        if (base_ss / diasaportes * 30) < salmin and base_ss > 0:
            ajuste = (((float(base_ss) * float(pepse) / 100) + float(salud_t)) + ((float(base_ss) * float(ppenem) / 100) + float(pension_t)))
            pension = ((float(base_ss) + float(suspension)) * float(ppene) / 100) + (float(suspension) * float(ppenem) / 100)
            base_arl = float(base_ss)
            base_caja = float(base_ss)
            arl = float(base_arl) * float(tararl) / 100
            ccf = float(base_caja) * float(pccf) / 100
            sena = 0
            icbf = 0
            variable = 0
        else:
            ajuste = 0

        if tipocontrato == 5:
            salud = salmin * (psalude / 100 + pepse / 100)

        totalap = float(salud) + float(pension) + float(arl) + float(ccf) + float(sena) + float(icbf) - float(salud_t) - float(pension_t) - float(pension_ft) + float(ajuste)
        provision = totalap + salud_t + pension_t
        fsp = calcular_descuento(int(base_ss), salmin)

        # Almacenar los valores en el diccionario `acumulados`
        acumulados[docidentidad] = {
                'documento': data.idcontrato.idempleado.docidentidad,
                'nombre': f"{data.idcontrato.idempleado.papellido} {data.idcontrato.idempleado.sapellido} {data.idcontrato.idempleado.pnombre} {data.idcontrato.idempleado.snombre}",
                'contrato': data.idcontrato.idcontrato,
                'idcosto': data.idcosto.idcosto,
                'salario': format_value(int(salario)),
                'diasaportes': format_value(int(diasaportes)) ,
                'base_ss': format_value(int(base_ss)) ,
                'base_arl': format_value(int(base_arl)) ,
                'base_caja': format_value(int(base_caja)) ,
                'pension_t': format_value(int(pension_t)) ,
                'pension_ft': format_value(int(pension_ft)) ,
                'salud_t': format_value(int(salud_t)) ,
                'variable': format_value(int(variable)) ,
                'suspension': format_value(int(suspension)) ,
                'salud': format_value(int(salud)) ,
                'pension': format_value(int(pension)) ,
                'arl': format_value(int(arl)) ,
                'ccf': format_value(int(ccf)) ,
                'sena': format_value(int(sena)) ,
                'icbf': format_value(int(icbf)) ,
                'ajuste': format_value(int(ajuste)) ,
                'totalap': format_value(int(totalap)) ,
                'provision': format_value(int(provision)) ,
                'fsp' : format_value(int(fsp)) ,
                'afp' : afp  ,
                'eps' : eps,
                'caja' : caja,
                
        
            }

    # Crear el archivo Excel
    wb = Workbook()
    ws = wb.active
    if acumulados:
        titulos = list(next(iter(acumulados.values())).keys())
        ws.append(titulos)  # Añadir los títulos al archivo Excel

    # Añadir los valores del diccionario acumulados
    for docidentidad, valores in acumulados.items():
        ws.append([valores[clave] for clave in titulos])
    # Guardar el archivo Excel en un buffer
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    # Devolver el archivo Excel como respuesta
    return buffer




