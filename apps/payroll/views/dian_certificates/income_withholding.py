from struct import pack_into
from traceback import print_tb
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Contratos, Crearnomina , Ingresosyretenciones ,Anos ,Conceptosdenomina, Nomina , Indicador
from apps.payroll.forms.PayrollForm import PayrollForm
from django.contrib import messages
from django.http import JsonResponse
from apps.components.humani import format_value
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from decimal import Decimal
import json
from django.http import QueryDict
from django.urls import reverse
from decimal import Decimal, ROUND_HALF_UP
from apps.components.close_employee_payroll import close_employee_payroll , guardar_historico_nomina
from django.db import transaction
from apps.components.salary import salario_mes
from apps.payroll.views.payroll.auto_recalculate import auto_recalculate
from django.db.models import Sum , Q
from collections import defaultdict
from urllib.parse import urlencode
from datetime import date
from django.utils import timezone
from openpyxl import Workbook
from django.http import HttpResponse


@login_required
@role_required('accountant')
def income_withholding_certificate(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    current_year = timezone.now().year  # O datetime.date.today().year
    years = Anos.objects.exclude(ano__exact=current_year).order_by('-ano')
    
    context = {
        'years': years,
    }
    
    # CAPTURAR GET
    anio = request.GET.get('anio')
    estado = request.GET.get('estado')

    if anio and estado :
        reten = Ingresosyretenciones.objects.filter(anoacumular__ano=anio, idempleado__estadocontrato = estado , id_empresa = idempresa)
        context['reten'] = reten
        

    
    return render(request, 'payroll/income_withholding.html', context)



@login_required
@role_required('accountant')
def generate_income_withholding_certificate(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    # Excluye año actual (2026), solo años cerrados
    current_year = timezone.now().year  # O datetime.date.today().year
    years = Anos.objects.exclude(ano__exact=current_year).order_by('-ano')
    
    context = {
        'years': years,
    }

    if request.method == "POST":
        try:
            anio = request.POST.get('anio')
            
            data = get_contratos_por_anio(anio,idempresa)
            certificado = data_certificate(data, anio , idempresa)
            
            reten = Ingresosyretenciones.objects.filter(anoacumular__ano=anio, idempleado__estadocontrato = 1 , id_empresa = idempresa)
            context['reten'] = reten

            messages.success(request, "Certificado generado correctamente.")

        except Exception as e:
            print(e)
            messages.error(request, "Error al generar el certificado.")

        url = reverse('payroll:income_withholding_certificate')
        params = urlencode({
            'anio': anio,
            'estado': 1
        })

        return redirect(f'{url}?{params}')
    
    
    return render(request, 'payroll/partials/generate_certificate.html', context)


@login_required
@role_required('accountant')
def generate_income_withholding_certificate_excel(request):
    if request.method == 'POST':

        usuario = request.session.get('usuario', {})
        idempresa = usuario['idempresa']

        year_init = request.POST.get('year')
        empresa = usuario['nombre_empresa'] 
        reten = Ingresosyretenciones.objects.filter(anoacumular__ano=year_init, id_empresa = idempresa)

        wb = Workbook()

        # ==========================================
        # HOJA 1 FORMULARIO 220
        # ==========================================


        ws = wb.active
        ws.title = "Formulario 220"

        headers = [
            'Id',
            'Tipo Documento',
            'Doc Identidad',
            'Nombre',
            'Salarios',
            'Honorarios',
            'Servicios',
            'Comisiones',
            'Prestaciones Sociales',
            'Viáticos',
            'Gastos de Representación',
            'Compensación CTA',
            'Cesantías e Intereses',
            'Pensiones',
            'Otros Pagos',
            'Fondo Cesantías',
            'Exceso Alimentación',
            'Cesantías Ley 90',
            'Apoyo Económico',
            'Total Ingresos Brutos',
            'Aportes Salud',
            'Aportes Pensión',
            'Aportes Voluntarios',
            'Aportes AFC',
            'Aportes AVC',
            'Retefuente Año'
        ]

    
        ws.append(headers)
        
        for item in reten:

            nombre_completo = " ".join(
                filter(None, [
                    item.idempleado.papellido,
                    item.idempleado.sapellido,
                    item.idempleado.pnombre,
                    item.idempleado.snombre
                ])
            )

            ws.append([
                item.idempleado.idempleado,
                item.idempleado.tipodocident.documento,
                item.idempleado.docidentidad,
                nombre_completo,

                item.salarios or 0,
                item.honorarios or 0,
                item.servicios or 0,
                item.comisiones or 0,
                item.prestacionessociales or 0,
                item.viaticos or 0,
                item.gastosderepresentacion or 0,
                item.compensacioncta or 0,
                item.cesantiasintereses or 0,
                item.pensiones or 0,
                item.otrospagos or 0,
                item.fondocesantias or 0,
                item.excesoalim or 0,
                item.cesantias90 or 0,
                item.apoyoeconomico or 0,
                item.totalingresosbrutos or 0,
                item.aportessalud or 0,
                item.aportespension or 0,
                item.aportesvoluntarios or 0,
                item.aportesafc or 0,
                item.aportesavc or 0,
                item.retefuente or 0,
            ])

        # ==========================================
        # HOJA 2 EXÓGENA
        # ==========================================

        ws2 = wb.create_sheet(title="Exogena")

        exogena = data_exogena(year_init, idempresa)

        if exogena:

            primer_empleado = next(iter(exogena.values()))

            columnas_devengado = list(
                primer_empleado.get('devengado', {}).keys()
            )

            columnas_otros = list(
                primer_empleado.get('otros_pagos', {}).keys()
            )

            headers_exogena = [
                'Cedula',
                'Nombre',
                *columnas_devengado,
                'Total Pagos Por Salarios',
                'vacaciones',
                'primas',
                'Total Prestaciones - Primas - Vacaciones',
                *columnas_otros
            ]

            ws2.append(headers_exogena)

            for cedula, info in exogena.items():

                fila = [
                    cedula,
                    info.get('nombre', '')
                ]

                # columnas dinámicas devengado
                for campo in columnas_devengado:
                    fila.append(
                        info.get('devengado', {}).get(campo, 0)
                    )

                # ESTE TOTAL FALTABA
                fila.append(
                    info.get('Total Pagos Por Salarios', 0)
                )

                fila.append(info.get('vacaciones', 0))
                fila.append(info.get('primas', 0))

                # ESTE TOTAL FALTABA
                fila.append(
                    info.get(
                        'Total Prestaciones - Primas - Vacaciones',
                        0
                    )
                )

                for campo in columnas_otros:
                    fila.append(
                        info.get('otros_pagos', {}).get(campo, 0)
                    )

                ws2.append(fila)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        response['Content-Disposition'] = (
            f'attachment; filename=informacion_exogena_{year_init}_{empresa}.xlsx'
        )

        wb.save(response)
        return response



def data_exogena(anio, idempresa):

    contratos_por_empleado = get_contratos_por_anio(anio, idempresa)

    resultado = {}

    for cedula, contratos in contratos_por_empleado.items():

        empleado_data = {
            'nombre': '',
            'devengado': {},
            'Total Pagos Por Salarios':0,
            'otros_pagos': {},
            'vacaciones': 0,
            'primas': 0,
            ''
            'Total Prestaciones - Primas - Vacaciones': 0,
        }

        for contrato in contratos:

            if not empleado_data['nombre']:
                empleado_data['nombre'] = " ".join(
                    filter(None, [
                        contrato.idempleado.papellido,
                        contrato.idempleado.sapellido,
                        contrato.idempleado.pnombre,
                        contrato.idempleado.snombre
                    ])
                )


            vacaciones = (returne_value_for_family(contrato.idcontrato,anio,'Vacaciones_Ausent') or 0)
            primas = (returne_value_for_concepto(contrato.idcontrato,anio,23) or 0)

            empleado_data['vacaciones'] += vacaciones
            empleado_data['primas'] += primas
            empleado_data['Total Prestaciones - Primas - Vacaciones'] += vacaciones + primas

            descontar = {
                'Licencia Remunerada': 82,
                'Ajuste - Retroactivo': 42
            }


            # =========================
            # DEVENGADO DINAMICO
            # =========================
            value = returne_value_family_exogena(contrato.idcontrato,anio,'basesegsocial',descontar)

            empleado_data['Total Pagos Por Salarios'] += value['salarios'] + value['Licencia Remunerada'] + value['Ajuste - Retroactivo']
            
            for concepto, valor in value.items():
                if concepto not in empleado_data['devengado']:
                    empleado_data['devengado'][concepto] = 0

                empleado_data['devengado'][concepto] += valor


            # =========================
            # OTROS PAGOS DINAMICOS
            # (si luego metes familias aquí)
            # =========================

            # ejemplo si después calculas otro diccionario:
            # otros = obtener_otros_pagos(...)
            # for concepto, valor in otros.items():
            #     if concepto not in empleado_data['otros_pagos']:
            #         empleado_data['otros_pagos'][concepto] = 0
            #     empleado_data['otros_pagos'][concepto] += valor


        resultado[cedula] = empleado_data

    return resultado


def returne_value_family_exogena(idcontrato, anio, familia, descontar):
    data = {}

    contrato = Contratos.objects.get(idcontrato=idcontrato)
    data['salarios'] = (returne_value_for_family(contrato.idcontrato, anio,familia ) or 0)

    for nombre, concepto in descontar.items():
        valor = (returne_value_for_concepto(contrato.idcontrato,anio,concepto) or 0 )
        data[nombre] = valor
        data['salarios'] -= valor

    return data




def data_certificate(data_contratos, anoacumular, idempresa):
    obj_anio = Anos.objects.get(ano=int(anoacumular))

    for cedula, contratos in data_contratos.items():

        # acumuladores por empleado
        data = {
            'salarios': 0,
            'honorarios': 0,
            'servicios': 0,
            'comisiones': 0,
            'prestacionessociales': 0,
            'viaticos': 0,
            'gastosderepresentacion': 0,
            'compensacioncta': 0,
            'cesantiasintereses': 0,
            'pensiones': 0,
            'totalingresosbrutos': 0,
            'aportessalud': 0,
            'aportespension': 0,
            'aportesvoluntarios': 0,
            'aportesafc': 0,
            'retefuente': 0,
            'otrospagos': 0,
            'fondocesantias': 0,
            'excesoalim': 0,
            'cesantias90': 0,
            'apoyoeconomico': 0,
            'aportesavc': 0,
            'ingresolaboralpromedio': 0,
        }

        idempleado = None

        for contrato in contratos:

            idempleado = contrato.idempleado.idempleado

            incapacidades = returne_value_for_family(contrato.idcontrato, anoacumular, 'incapacidad') or 0
            vacaciones = returne_value_for_family(contrato.idcontrato, anoacumular, 'Vacaciones_Ausent') or 0

            salarios = returne_value_for_family(contrato.idcontrato, anoacumular, 'basesegsocial') or 0
            honorarios = returne_value_for_family(contrato.idcontrato, anoacumular, 'honorarios') or 0
            servicios = returne_value_for_family(contrato.idcontrato, anoacumular, 'servicios') or 0
            comisiones = returne_value_for_family(contrato.idcontrato, anoacumular, 'comisiones') or 0
            prestacionessociales = returne_value_for_family(contrato.idcontrato, anoacumular, 'prestacionsocial') or 0
            viaticos = returne_value_for_family(contrato.idcontrato, anoacumular, 'viaticos') or 0
            gastos = returne_value_for_family(contrato.idcontrato, anoacumular, 'gastosderepresentacion') or 0
            compensacion = returne_value_for_family(contrato.idcontrato, anoacumular, 'compensacioncta') or 0
            cesantias_int = returne_value_for_concepto(contrato.idcontrato, int(anoacumular) - 1,821 ) or 0
            pensiones = returne_value_for_family(contrato.idcontrato, anoacumular, 'pension') or 0
            aportessalud = returne_value_for_family(contrato.idcontrato, anoacumular, 'aportessalud') or 0
            aportespension = returne_value_for_family(contrato.idcontrato, anoacumular, 'aportespension') or 0
            aportesvoluntarios = returne_value_for_concepto(contrato.idcontrato, anoacumular,53 ) or 0

            cesantias90 = returne_value_for_concepto(contrato.idcontrato, anoacumular,820 ) or 0
            otros_pagos = returne_value_for_family(contrato.idcontrato, anoacumular, 'otrospagos') or 0
            apoyoeconomico = returne_value_for_family(contrato.idcontrato, anoacumular, 'apoyoeconomico') or 0

            sumatoria = calculate_6_month_taxable_income_average(contrato.idcontrato, anoacumular) or 0
            
            # acumular
            data['salarios'] += (salarios - vacaciones - incapacidades)
            data['honorarios'] += honorarios
            data['servicios'] += servicios
            data['comisiones'] += comisiones
            data['prestacionessociales'] += prestacionessociales
            data['viaticos'] += viaticos
            data['gastosderepresentacion'] += gastos
            data['compensacioncta'] += compensacion
            data['cesantiasintereses'] += cesantias_int
            data['pensiones'] += pensiones
            data['aportessalud'] += aportessalud
            data['aportespension'] += aportespension
            data['aportesvoluntarios'] += aportesvoluntarios
            data['cesantias90'] += cesantias90
            data['otrospagos'] += otros_pagos
            data['ingresolaboralpromedio'] += sumatoria
        # cálculo final


        data['totalingresosbrutos'] = (
            data['salarios'] + data['honorarios'] + data['servicios'] + data['comisiones'] + data['otrospagos'] + 
            data['prestacionessociales'] + data['viaticos'] + data['gastosderepresentacion'] + data['compensacioncta'] + 
            data['cesantiasintereses'] + data['pensiones'] +  data['apoyoeconomico']
        )

        # guardar UNA sola vez por empleado
        Ingresosyretenciones.objects.update_or_create(
            idempleado_id=idempleado,
            anoacumular=obj_anio,
            id_empresa_id=idempresa,
            defaults=data
        )

    return True










def returne_value_for_family(idcontrato, anoacumular, familia):
    total = 0

    data = Nomina.objects.filter(
        idnomina__anoacumular__ano=int(anoacumular),
        idcontrato_id=int(idcontrato),
        idconcepto__indicador__nombre=familia,
    )

    for item in data:
        total += abs(item.valor)

    return total


def returne_value_for_concepto(idcontrato, anoacumular, concepto):
    total = 0

    data = Nomina.objects.filter(
        idnomina__anoacumular__ano=int(anoacumular),
        idcontrato_id=int(idcontrato),
        idconcepto__codigo=concepto,
    )

    for item in data:
        total += abs(item.valor)

    return total


def get_contratos_por_anio(anio, empresa_id):
    contratos = Contratos.objects.filter(
        Q(id_empresa=empresa_id) &
        (
            Q(fechainiciocontrato__year=anio) |
            Q(fechafincontrato__year=anio)
        )
    ).select_related('idempleado')

    resultado = defaultdict(list)

    for contrato in contratos:
        if contrato.idempleado:
            cedula = contrato.idempleado.docidentidad
            resultado[cedula].append(contrato)

    return resultado



def calculate_6_month_taxable_income_average(idcontrato, anoacumular):
    total = 0
    meses_division = 0
    anoacumular = int(anoacumular)

    MONTHS = {
        1:'ENERO',2:'FEBRERO',3:'MARZO',4:'ABRIL',
        5:'MAYO',6:'JUNIO',7:'JULIO',8:'AGOSTO',
        9:'SEPTIEMBRE',10:'OCTUBRE',11:'NOVIEMBRE',12:'DICIEMBRE'
    }

    contrato = Contratos.objects.get(idcontrato=idcontrato)

    inicio_contrato = contrato.fechainiciocontrato
    fin_contrato = contrato.fechafincontrato or date.max


    mes_final = 12
    mes_inicial = 7
    ano_previo = anoacumular

    if fin_contrato <= date(anoacumular,12,31):
        mes_final = fin_contrato.month
        mes_inicial_calc = max(1, mes_final-5)

        if mes_inicial_calc <= 0:
            mes_inicial_calc += 12
            ano_previo -= 1

        mes_inicial = mes_inicial_calc


    mes_inicio_contrato = inicio_contrato.month

    if mes_inicial < mes_inicio_contrato:
        mes_inicial = mes_inicio_contrato


    meses_promedio = mes_final - mes_inicial + 1

    if meses_promedio < 0:
        meses_promedio += 12


    if meses_promedio == 0:
        return 0


    mes_actual = mes_inicial
    ano_actual = ano_previo


    for _ in range(meses_promedio):

        nombre_mes = MONTHS[mes_actual]

        ingreso_mes = (
            Nomina.objects.filter(
                idcontrato=contrato,
                idnomina__tiponomina__idtiponomina__in=[1,2,3,4,5,6,7,8,9,11,12], # tipos de nomina
                idnomina__mesacumular=nombre_mes,
                idnomina__anoacumular__ano=ano_actual,
                idconcepto__indicador__nombre='ingresotributario'
            )
            .aggregate(total=Sum('valor'))['total']
            or 0
        )

        if ingreso_mes > 0:
            meses_division += 1

        total += ingreso_mes

        mes_actual += 1

        if mes_actual > 12:
            mes_actual = 1
            ano_actual += 1


    promedio = (
        total / meses_division
        if meses_division > 0 else 0
    )

    return promedio