from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Tipodenomina , Liquidacion , EditHistory , Conceptosfijos , Salariominimoanual,Conceptosdenomina , Empresa , Anos , Nomina , Contratos
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
from decimal import Decimal, ROUND_HALF_UP , getcontext , ROUND_CEILING , ROUND_UP
from django.db.models import Sum, Count, Q
from apps.payroll.views.payroll.payroll_automatic_systems import calcular_dias, precargar_acumulados




@login_required
@role_required('accountant')
def UgppPayrollAudit(request,payroll_id):
    data = {}
    payroll = Crearnomina.objects.get(idnomina=payroll_id)
    salaries = get_audit_salaries(payroll_id)
    contributions = get_audit_contributions(payroll_id)
    total_errors , errors_list = get_audit_total_errors(payroll_id)

    data = {
        'payroll': payroll,
        'salaries': salaries,
        'contributions': contributions,
        'total_employees': get_audit_employees(payroll_id),
        'total_to_pay': get_audit_total_to_pay(payroll_id),
        'total_errors': total_errors,
        'errors_list': errors_list,
    }
    return render(request, './payroll/UgppPayrollAudit.html', data)


def get_audit_total_errors(payroll_id):

    errors_count = 0
    errors_list = []

    errors_count1 , errors_list1 = error_salary_audit(payroll_id)
    errors_count2 , errors_list2 = error_contributions_audit(payroll_id)
    errors_count3 , errors_list3 = error_transport_audit(payroll_id)
    
    errors_count = errors_count1 + errors_count2 + errors_count3
    errors_list = errors_list1 + errors_list2 + errors_list3

    return errors_count , errors_list


def error_salary_audit(payroll_id):

    errors_count = 0
    errors_list = []
    contratos_cache = {}

    getcontext().prec = 50

    nomina = Crearnomina.objects.select_related('anoacumular').get(idnomina=payroll_id)

    salario_anual = Salariominimoanual.objects.get(ano=nomina.anoacumular.ano)
    sal_min = salario_anual.salariominimo
    aux_tra = salario_anual.auxtransporte

    mes = nomina.fechainicial.month
    anio = nomina.fechainicial.year

    conceptos = [1, 4, 33, 34]

    registros = Nomina.objects.select_related(
        'idcontrato__idempleado',
        'idconcepto'
    ).filter(
        idnomina_id=payroll_id,
        idconcepto__codigo__in=conceptos,
        estadonomina=1
    )

    for data in registros:

        contrato = data.idcontrato
        empleado = contrato.idempleado
        codigo = data.idconcepto.codigo
        contrato_id = contrato.idcontrato

        # ==========================================
        # CACHE POR CONTRATO
        # ==========================================
        if contrato_id not in contratos_cache:
            salario = salario_mes(contrato, mes, anio)
            acumulados = precargar_acumulados(nomina, contrato_id)

            contratos_cache[contrato_id] = {
                "salario": Decimal(salario),
                "acumulados": acumulados
            }

        salario = contratos_cache[contrato_id]["salario"]
        acumulados = contratos_cache[contrato_id]["acumulados"]

        # ==========================================
        # DIAS
        # ==========================================
        diasnomina = calcular_dias(contrato, nomina, codigo, acumulados)

        # ==========================================
        # VALIDACIONES BASE
        # ==========================================
        valor = Decimal('0')

        valor = (
            salario * Decimal(diasnomina) / Decimal('30')
        ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        # ==========================================
        # ERROR 1: VALOR INCORRECTO
        # ==========================================
        if data.cantidad != diasnomina:
            errors_list.append(
                f"[BASE] {contrato_id} → "
                f"Días incorrectos ({data.cantidad} vs {diasnomina}) "
                f"→ Esto afecta el salario ({data.valor} vs {valor})"
            )
            errors_count += 1

        elif data.valor != valor:
            errors_list.append(
                f"[SALARIO] {contrato_id} → "
                f"Actual: {data.valor} | Esperado: {valor}"
            )
            errors_count += 1

        # ==========================================
        # VALIDACIONES UGPP
        # ==========================================

        # ERROR 3: SALARIO POR DEBAJO DEL MINIMO
        if codigo == 1 and salario < sal_min:
            errors_list.append(
                f"[MINIMO] {contrato_id} "
                f"tiene salario menor al mínimo ({salario} < {sal_min})"
            )
            errors_count += 1

        # ERROR 4: DIAS MAYORES A 30
        if diasnomina > 30:
            errors_list.append(
                f"[DIAS_EXCESO] {contrato_id} "
                f"tiene más de 30 días ({diasnomina})"
            )
            errors_count += 1

        # ERROR 5: APRENDIZ MAL LIQUIDADO
        if codigo in [33, 34] and salario >= sal_min:
            errors_list.append(
                f"[APRENDIZ] {contrato_id} "
                f"tiene salario de aprendiz sospechoso ({salario})"
            )
            errors_count += 1

        # ERROR 6: SALARIO INTEGRAL BAJO (13 SMMLV aprox)
        if codigo == 4 and salario < (sal_min * 13):
            errors_list.append(
                f"[INTEGRAL] {contrato_id} "
                f"tiene salario integral bajo ({salario})"
            )
            errors_count += 1

    return errors_count, errors_list


def error_transport_audit(payroll_id):

    errors_count = 0
    errors_list = []
    contratos_cache = {}

    getcontext().prec = 50

    nomina = Crearnomina.objects.select_related('anoacumular').get(idnomina=payroll_id)

    salario_anual = Salariominimoanual.objects.get(ano=nomina.anoacumular.ano)
    sal_min = salario_anual.salariominimo
    aux_tra = salario_anual.auxtransporte

    mes = nomina.fechainicial.month
    anio = nomina.fechainicial.year

    # SOLO TRANSPORTE
    registros = Nomina.objects.select_related(
        'idcontrato',
        'idconcepto'
    ).filter(
        idnomina_id=payroll_id,
        idconcepto__codigo=2,
        estadonomina=1
    )

    for data in registros:

        contrato = data.idcontrato
        contrato_id = contrato.idcontrato
        codigo = 2

        # ==========================================
        # CACHE POR CONTRATO
        # ==========================================
        if contrato_id not in contratos_cache:

            salario = salario_mes(contrato, mes, anio)
            acumulados = precargar_acumulados(nomina, contrato_id)

            contratos_cache[contrato_id] = {
                "salario": Decimal(salario),
                "acumulados": acumulados
            }

        salario = contratos_cache[contrato_id]["salario"]
        acumulados = contratos_cache[contrato_id]["acumulados"]

        # ==========================================
        # DIAS
        # ==========================================
        diasnomina = calcular_dias(contrato, nomina, codigo, acumulados)

        # ==========================================
        # VALIDACIONES 
        # ==========================================

        # 1. SI SALARIO >= 2 SMMLV → NO DEBE EXISTIR
        if salario >= (sal_min * 2):
            errors_list.append(
                f"[TRANSPORTE] {contrato_id} → "
                f"No debería tener auxilio (salario {salario} >= 2 SMMLV)"
            )
            errors_count += 1
            continue

        # BASE TRANSPORTE
        total_base_trans = Nomina.objects.filter(
            idcontrato=contrato,
            idnomina_id=payroll_id,
            estadonomina=1,
            idconcepto__indicador__nombre='basetransporte'
        ).exclude(
            idconcepto__codigo=2
        ).aggregate(total=Sum('valor'))['total'] or 0

        # 2. BASE <= 0 → NO DEBE EXISTIR
        if total_base_trans <= 0:
            errors_list.append(
                f"[TRANSPORTE] {contrato_id} → "
                f"No debería existir (base transporte = {total_base_trans})"
            )
            errors_count += 1
            continue

        # 3. BASE >= 2 SMMLV → NO DEBE EXISTIR
        if total_base_trans >= (sal_min * 2):
            errors_list.append(
                f"[TRANSPORTE] {contrato_id} → "
                f"No debería existir (base transporte >= 2 SMMLV)"
            )
            errors_count += 1
            continue

        # ==========================================
        # CALCULO ESPERADO
        # ==========================================
        valor_esperado = (
            Decimal(diasnomina) *
            (Decimal(aux_tra) / Decimal('30'))
        ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        # ==========================================
        # ERRORES
        # ==========================================
        if data.cantidad != diasnomina:
            errors_list.append(
                f"[TRANSPORTE_DIAS] {contrato_id} → "
                f"Actual: {data.cantidad} | Esperado: {diasnomina}"
            )
            errors_count += 1

        elif data.valor != valor_esperado:
            errors_list.append(
                f"[TRANSPORTE_VALOR] {contrato_id} → "
                f"Actual: {data.valor} | Esperado: {valor_esperado}"
            )
            errors_count += 1

    return errors_count, errors_list


def error_contributions_audit(payroll_id):

    errors_count = 0
    errors_list = []
    contratos_cache = {}

    getcontext().prec = 50

    nomina = Crearnomina.objects.select_related('anoacumular').get(idnomina=payroll_id)

    # ==========================================
    # PARAMETROS
    # ==========================================
    EPS = Conceptosfijos.objects.get(idfijo=8)
    AFP = Conceptosfijos.objects.get(idfijo=10)
    tope_ibc = Conceptosfijos.objects.get(idfijo=2)
    factor_integral = Conceptosfijos.objects.get(idfijo=1).valorfijo

    # FSP
    fsp416 = Conceptosfijos.objects.get(idfijo=12).valorfijo
    fsp1617 = Conceptosfijos.objects.get(idfijo=13).valorfijo
    fsp1718 = Conceptosfijos.objects.get(idfijo=14).valorfijo
    fsp1819 = Conceptosfijos.objects.get(idfijo=15).valorfijo
    fsp1920 = Conceptosfijos.objects.get(idfijo=16).valorfijo
    fsp21 = Conceptosfijos.objects.get(idfijo=17).valorfijo

    sal_min = Salariominimoanual.objects.get(
        ano=nomina.anoacumular.ano
    ).salariominimo

    # ==========================================
    # TRAER APORTES
    # ==========================================
    registros = Nomina.objects.select_related(
        'idcontrato',
        'idconcepto'
    ).filter(
        idnomina_id=payroll_id,
        estadonomina=1,
        idconcepto__codigo__in=[60, 70, 90]
    )

    for data in registros:

        contrato = data.idcontrato
        contrato_id = contrato.idcontrato
        codigo = data.idconcepto.codigo

        # ==========================================
        # CACHE POR CONTRATO
        # ==========================================
        if contrato_id not in contratos_cache:

            total_base_ss = Nomina.objects.filter(
                idcontrato=contrato,
                idnomina_id=payroll_id,
                estadonomina=1,
                idconcepto__indicador__nombre='basesegsocial'
            ).exclude(
                idconcepto__codigo__in=[60, 70, 90]
            ).aggregate(total=Sum('valor'))['total'] or 0

            # BASE FSP (ACUMULADA)
            base_ss_fsp = Nomina.objects.filter(
                idcontrato=contrato,
                idnomina__mesacumular=nomina.mesacumular,
                idnomina__anoacumular=nomina.anoacumular,
                idconcepto__indicador__nombre='basesegsocial'
            ).exclude(
                idconcepto__codigo__in=[60, 70, 90]
            ).aggregate(total=Sum('valor'))['total'] or 0

            # INTEGRAL
            if contrato.tiposalario.idtiposalario == 2:
                total_base_ss *= (factor_integral / 100)
                base_ss_fsp2 = base_ss_fsp * Decimal('0.7')
            else:
                base_ss_fsp2 = base_ss_fsp

            base_max = sal_min * tope_ibc.valorfijo
            base_ss = min(total_base_ss, base_max)

            base_ss = Decimal(base_ss).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            contratos_cache[contrato_id] = {
                "base_ss": base_ss,
                "base_ss_fsp2": Decimal(base_ss_fsp2)
            }

        base_ss = contratos_cache[contrato_id]["base_ss"]
        base_ss_fsp2 = contratos_cache[contrato_id]["base_ss_fsp2"]

        # ==========================================
        # CALCULO ESPERADO
        # ==========================================

        # EPS
        if codigo == 60:
            valor_esperado = (
                base_ss * Decimal(EPS.valorfijo) / Decimal('100')
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            valor_esperado = -1 * valor_esperado

        # PENSION
        elif codigo == 70:
            valor_esperado = (
                base_ss * Decimal(AFP.valorfijo) / Decimal('100')
            ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            if contrato.pensionado == '2':
                valor_esperado = Decimal('0')

            valor_esperado = -1 * valor_esperado

        # FSP
        elif codigo == 90:

            # Determinar porcentaje
            if base_ss_fsp2 <= (sal_min * 4):
                FSP = 0
            elif base_ss_fsp2 > (sal_min * 20):
                FSP = fsp21
            elif base_ss_fsp2 > (sal_min * 19):
                FSP = fsp1920
            elif base_ss_fsp2 > (sal_min * 18):
                FSP = fsp1819
            elif base_ss_fsp2 > (sal_min * 17):
                FSP = fsp1718
            elif base_ss_fsp2 > (sal_min * 16):
                FSP = fsp1617
            elif base_ss_fsp2 > (sal_min * 4):
                FSP = fsp416
            else:
                FSP = 0

            if FSP > 0:
                valor_esperado = (
                    base_ss_fsp2 * Decimal(FSP) / Decimal('100')
                ).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            else:
                valor_esperado = Decimal('0')

            if contrato.pensionado == '2':
                valor_esperado = Decimal('0')

            valor_esperado = -1 * valor_esperado

        else:
            continue

        # ==========================================
        # ERRORES
        # ==========================================
        if data.valor != valor_esperado:
            errors_list.append(
                f"[APORTE] {contrato_id} → "
                f"Cod:{codigo} | Actual: {data.valor} | Esperado: {valor_esperado}"
            )
            errors_count += 1


    return errors_count, errors_list




def get_audit_salaries(payroll_id):

    queryset = Nomina.objects.filter(
        idnomina_id=payroll_id,
        estadonomina=1
    )

    data = queryset.aggregate(
        normales=Sum('valor', filter=Q(idconcepto__codigo=1)),
        normales_count=Count('idregistronom', filter=Q(idconcepto__codigo=1)),

        integral=Sum('valor', filter=Q(idconcepto__codigo=4)),
        integral_count=Count('idregistronom', filter=Q(idconcepto__codigo=4)),

        aprendices=Sum('valor', filter=Q(idconcepto__codigo__in=[33, 34])),
        aprendices_count=Count('idregistronom', filter=Q(idconcepto__codigo__in=[33, 34])),

        otros=Sum('valor', filter=Q(idconcepto__codigo=41)),
        otros_count=Count('idregistronom', filter=Q(idconcepto__codigo=41)),
    )

    # limpiar None → 0
    return {k: v or 0 for k, v in data.items()}
    

def get_audit_contributions(payroll_id):

    queryset = Nomina.objects.filter(
        idnomina_id=payroll_id,
        estadonomina=1
    )

    data = queryset.aggregate(
        eps=Sum('valor', filter=Q(idconcepto__codigo=60)),
        eps_count=Count('idregistronom', filter=Q(idconcepto__codigo=60)),

        pension=Sum('valor', filter=Q(idconcepto__codigo=70)),
        pension_count=Count('idregistronom', filter=Q(idconcepto__codigo=70)),

        incapacidades=Sum('valor', filter=Q(idconcepto__codigo__in=[25, 26, 27, 28])),
        incapacidades_count=Count('idregistronom', filter=Q(idconcepto__codigo__in=[25, 26, 27, 28])),
    )

    return {k: v or 0 for k, v in data.items()}


def get_audit_employees(payroll_id):
    queryset = Nomina.objects \
        .select_related('idcontrato') \
        .filter(idnomina=payroll_id, estadonomina=1) \
        .values(
            'idcontrato'
        ) \
        .distinct()

    return queryset.count()


def get_audit_total_to_pay(payroll_id):
    queryset = Nomina.objects.filter(
        idnomina_id=payroll_id,
        estadonomina=1
    )
    return queryset.aggregate(total=Sum('valor'))['total'] or 0
