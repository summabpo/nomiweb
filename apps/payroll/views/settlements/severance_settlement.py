from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import NovFijos , Conceptosdenomina , Contratos , Indicador, Liquidacion , Salariominimoanual , Nomina,Vacaciones
from django.http import HttpResponse
from django.urls import reverse
from apps.payroll.forms.SettlementForm import SettlementForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime , date
from .liquidacion_utils import *
from django.db.models import Q

@login_required
@role_required('accountant')
def settlement_list(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    settlements = Liquidacion.objects.filter(idcontrato__id_empresa = idempresa ).order_by('idliquidacion')
    return render(request, './payroll/settlement_list.html',{'settlements': settlements})

@login_required
@role_required('accountant')
def settlement_create(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    form = SettlementForm(idempresa = idempresa)
    
    return render(request, './payroll/partials/settlement_create.html',{'form': form})



@require_POST
def settlement_calculate(request):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    
    contract_id = request.POST.get('contract')
    end_date_str = request.POST.get('end_date')
    reason = request.POST.get('reason_for_termination')

    if not (contract_id and end_date_str and reason):
        return JsonResponse({'error': 'Datos incompletos'}, status=400)

    try:
        contrato = Contratos.objects.get(idcontrato=contract_id)
        fecha_inicio = contrato.fechainiciocontrato
        fecha_fin = datetime.strptime(end_date_str, '%d-%m-%Y').date()
    except Contratos.DoesNotExist:
        return JsonResponse({'error': 'Contrato no encontrado'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)

    if fecha_fin < fecha_inicio:
        return JsonResponse({'error': 'La fecha final debe ser posterior al inicio del contrato'}, status=400)

    # Datos base
    salario = contrato.salario
    salario_min_obj = Salariominimoanual.objects.filter(ano=fecha_fin.year).first()
    if not salario_min_obj:
        return JsonResponse({'error': 'No hay salario mínimo definido para ese año'}, status=400)

    salario_minimo = salario_min_obj.salariominimo
    aux_transporte = 0 if salario > (2 * salario_minimo) else salario_min_obj.auxtransporte

    dias_trabajados = dias_360(fecha_inicio, fecha_fin)
    fecha_cesantias = obtener_fecha_cesantias(fecha_inicio, fecha_fin)
    dias_cesantias = dias_360_2(fecha_cesantias, fecha_fin)

    fecha_prima = obtener_fecha_prima(fecha_inicio, fecha_fin)
    dias_prima = dias_360_2(fecha_prima, fecha_fin)

    # Conceptos
    extras_y_comisiones_qs = Conceptosdenomina.objects.filter(Q(indicador__nombre='extras') | Q(indicador__nombre='comisiones') ,id_empresa = idempresa)
    suspensiones_qs = Conceptosdenomina.objects.filter( indicador__nombre = 'suspcontrato',id_empresa = idempresa)
    recargos_qs = Conceptosdenomina.objects.filter(codigo=3 ,id_empresa = idempresa )

    # Acumulados
    acum_cesantias = acumular_por_mes(Nomina, extras_y_comisiones_qs, contrato.idcontrato, fecha_fin.year, fecha_cesantias.month, fecha_fin.month)
    acum_prima = acumular_por_mes(Nomina, extras_y_comisiones_qs, contrato.idcontrato, fecha_fin.year, fecha_prima.month, fecha_fin.month)
    acum_susp = acumular_por_mes(Nomina, suspensiones_qs, contrato.idcontrato, fecha_fin.year, fecha_cesantias.month, fecha_fin.month, campo='cantidad')
    acum_recargos = acumular_por_mes(Nomina, recargos_qs, contrato.idcontrato, fecha_fin.year, fecha_cesantias.month, fecha_fin.month)

    # Días efectivos
    dias_efectivos_cesantias = dias_cesantias - acum_susp
    dias_efectivos_prima = dias_prima - acum_susp

    # Bases
    base_cesantias = calcular_base_promedio(acum_cesantias, dias_efectivos_cesantias, salario, aux_transporte)
    base_prima = calcular_base_promedio(acum_prima, dias_efectivos_prima, salario, aux_transporte)
    base_vacaciones = calcular_base_vacaciones(acum_recargos, dias_cesantias, salario)

    # Vacaciones
    dias_susp_vac = Nomina.objects.filter(
        idcontrato=contrato.idcontrato,
        estadonomina=2,
        idconcepto__id_empresa = idempresa,
        idconcepto__indicador__nombre='suspcontrato'
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    dias_vac_generados = (dias_trabajados - dias_susp_vac) * 15 / 360
    dias_vac_tomados = Vacaciones.objects.filter(idcontrato=contrato.idcontrato).aggregate(total=Sum('diasvac'))['total'] or 0
    dias_vacaciones = round(dias_vac_generados - (dias_vac_tomados or 0), 2)

    # Componentes de liquidación
    prima = calcular_prima(dias_prima, base_prima)
    cesantias = calcular_cesantias(dias_efectivos_cesantias, base_cesantias)
    vacaciones = calcular_vacaciones(dias_vacaciones, base_vacaciones)
    intereses = calcular_intereses_cesantias(dias_cesantias, cesantias)
    indemnizacion = calcular_indemnizacion(salario, dias_trabajados, reason)

    total_liquidacion = prima + cesantias + vacaciones + intereses + indemnizacion

    return JsonResponse({
        'dias_trabajados': safe_value(dias_trabajados),
        'dias_prima': safe_value(dias_prima),
        'dias_cesantias': safe_value(dias_cesantias),
        'dias_vacaciones': safe_value(dias_vacaciones),
        'salario': safe_value(salario),
        'aux_transporte': safe_value(aux_transporte),
        'base_prima': safe_value(base_prima),
        'base_cesantias': safe_value(base_cesantias),
        'base_vacaciones': safe_value(base_vacaciones),
        'prima': safe_value(prima),
        'cesantias': safe_value(cesantias),
        'vacaciones': safe_value(vacaciones),
        'intereses': safe_value(intereses),
        'indemnizacion': safe_value(indemnizacion),
        'total_liquidacion': safe_value(total_liquidacion),
        'inicio_contrato': fecha_inicio or "",  # Aquí podrías usar "" si prefieres string vacío para fechas
        'fin_contrato': fecha_fin or "",
        'dias_susp_vac':dias_susp_vac,
    })


