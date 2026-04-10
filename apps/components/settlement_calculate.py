
from math import ceil

from apps.common.models import Tipodenomina , Conceptosdenomina ,Nomina, Crearnomina , Contratos , Anos, Liquidacion , Salariominimoanual , Nomina,Vacaciones
from apps.payroll.views.settlements.liquidacion_utils import *
from django.db.models import Sum
from datetime import datetime , date
def settlement_calculate_data(contract_id , end_date , reason):

    data = {
        'dias_trabajados': 0,
        'dias_prima':0,
        'dias_cesantias':0,
        'dias_vacaciones': 0,
        'dias_susp_vac':0,
        'dias_susp_ces':0,
        'salario': 0,
        'aux_transporte': 0,
        'base_prima': 0,
        'base_cesantias': 0,
        'base_vacaciones': 0,
        'prima': 0,
        'cesantias': 0,
        'vacaciones': 0,
        'intereses': 0,
        'indemnizacion': 0,
        'total_liquidacion': 0,
        'inicio_contrato': 0,  
        'fin_contrato': 0,
        'dias_brutos_cesantias': 0,
    }
    if not (contract_id and end_date and reason):
        return data 

    try:
        contrato = Contratos.objects.select_related('tiposalario').get(idcontrato=contract_id)
        fecha_inicio = contrato.fechainiciocontrato
        fecha_fin = datetime.strptime(end_date, '%Y-%m-%d').date()
    except:
        return data 

    # Datos base
    salario = contrato.salario
    salario_min_obj = Salariominimoanual.objects.filter(ano=fecha_fin.year).first()

    if not salario_min_obj:
        return data 
    


    dias_trabajados = dias_360(fecha_inicio, fecha_fin)
    fecha_cesantias = obtener_fecha_cesantias(fecha_inicio, fecha_fin)
    dias_cesantias = dias_360_2(fecha_cesantias, fecha_fin) 

    fecha_prima = obtener_fecha_prima(fecha_inicio, fecha_fin)
    dias_prima = dias_360_2(fecha_prima, fecha_fin) 


    salario_minimo = salario_min_obj.salariominimo
    aux_transporte = 0 if salario > (2 * salario_minimo) else salario_min_obj.auxtransporte

    es_integral = contrato.tiposalario_id == 2

    if contrato.tipocontrato_id == 6:
        indemnizacion = calcular_indemnizacion(salario, dias_trabajados, reason, fecha_fin)
        data.update({
            'inicio_contrato': fecha_inicio or "",
            'fin_contrato': fecha_fin or "",
            'salario': safe_value(salario),
            'aux_transporte': safe_value(aux_transporte),
            'dias_trabajados': safe_value(dias_trabajados),
            'dias_prima': 0,
            'dias_cesantias': 0,
            'dias_vacaciones': 0,
            'base_prima': 0,
            'base_cesantias': 0,
            'base_vacaciones': safe_value(ceil(salario)) if salario else 0,
            'prima': 0,
            'cesantias': 0,
            'vacaciones': 0,
            'intereses': 0,
            'indemnizacion': safe_value(indemnizacion),
            'total_liquidacion': safe_value(indemnizacion),
            'dias_susp_vac': 0,
            'dias_susp_ces': 0,
            'dias_brutos_cesantias': 0,
        })
        return data

    suspensiones_qs = Conceptosdenomina.objects.filter(
        indicador__nombre='suspcontrato',
        id_empresa=contrato.id_empresa,
    )
    basecesantias_qs = Conceptosdenomina.objects.filter(
        indicador__nombre='basecesantias',
        id_empresa=contrato.id_empresa,
    )
    baseprima_qs = Conceptosdenomina.objects.filter(
        indicador__nombre='baseprima',
        id_empresa=contrato.id_empresa,
    )
    basevacaciones_qs = Conceptosdenomina.objects.filter(
        indicador__nombre='basevacaciones',
        id_empresa=contrato.id_empresa,
    )

    # Acumulado variable cesantías: 1-ene año retiro o desde ingreso (fecha_cesantias) → retiro
    acum_cesantias = acumular_por_mes(
        Nomina,
        basecesantias_qs,
        contrato.idcontrato,
        fecha_cesantias.year,
        fecha_cesantias.month,
        fecha_fin.year,
        fecha_fin.month,
    )
    # Acumulado variable prima: semestre en curso o desde ingreso si es posterior al inicio del semestre
    ap_ano_i, ap_mes_i, ap_ano_f, ap_mes_f = rango_meses_acumulacion_prima_semestre(fecha_inicio, fecha_fin)
    acum_prima = acumular_por_mes(
        Nomina,
        baseprima_qs,
        contrato.idcontrato,
        ap_ano_i,
        ap_mes_i,
        ap_ano_f,
        ap_mes_f,
    )
    # Suspensiones: desde 1 enero del año de retiro o desde ingreso si es posterior (misma ventana que días cesantías).
    acum_susp_ces_periodo = acumular_por_mes(
        Nomina,
        suspensiones_qs,
        contrato.idcontrato,
        fecha_cesantias.year,
        fecha_cesantias.month,
        fecha_fin.year,
        fecha_fin.month,
        campo="cantidad",
    )
    # Suspensiones para vacaciones: todo el contrato hasta la fecha de terminación.
    acum_susp_contrato = acumular_por_mes(
        Nomina,
        suspensiones_qs,
        contrato.idcontrato,
        fecha_inicio.year,
        fecha_inicio.month,
        fecha_fin.year,
        fecha_fin.month,
        campo="cantidad",
    )
    bv_ano_i, bv_mes_i, bv_ano_f, bv_mes_f = rango_meses_acumulacion_basevacaciones_12m(fecha_inicio, fecha_fin)
    acum_recargos = acumular_por_mes(
        Nomina,
        basevacaciones_qs,
        contrato.idcontrato,
        bv_ano_i,
        bv_mes_i,
        bv_ano_f,
        bv_mes_f,
    )
    
    #acum_susp = acum_prima = acum_cesantias = 0 



    # Días brutos cesantías (intereses no disminuyen por suspensiones / licencias no remuneradas)
    dias_cesantias_brutos = dias_cesantias

    # Días efectivos (liquidación de cesantías en dinero)
    dias_efectivos_cesantias = dias_cesantias_brutos - acum_susp_ces_periodo
    dias_efectivos_prima = dias_prima

    # Bases
    base_cesantias = calcular_base_promedio(acum_cesantias, dias_efectivos_cesantias, salario, aux_transporte)
    base_prima = calcular_base_promedio(acum_prima, dias_efectivos_prima, salario, aux_transporte)
    fecha_desde_base_vac = fecha_desde_rango_acumulacion_vacaciones(fecha_inicio, fecha_fin)
    dias_periodo_base_vac = dias_360(fecha_desde_base_vac, fecha_fin)
    base_vacaciones = calcular_base_vacaciones(acum_recargos, dias_periodo_base_vac, salario)

    # Vacaciones — días de suspensión mostrados para cesantías = acumulado del periodo de cesantías
    dias_susp_ces = float(acum_susp_ces_periodo or 0)

    resultado = depurar_suspension_contrato(contrato, suspensiones_qs)

    # Imprimir total de días de suspensión
    #print("Total días de suspensión:", resultado["total_dias_susp"])

    # Imprimir detalle registro por registro
    for reg in resultado["detalle"]:
        print(f"Nómina ID: {reg['nomina_id']}, Concepto: {reg['concepto']}, "
            f"Código: {reg['codigo']}, Días: {reg['dias_susp']}, Valor: {reg['valor']}")
    
    dias_vac = depurar_vacaciones(contrato)
    dias_trabajados = float(dias_trabajados or 0)
    dias_vac = float(dias_vac or 0)
    acum_susp_contrato_f = float(acum_susp_contrato or 0)

    dias_vac_generados = (dias_trabajados - dias_vac - acum_susp_contrato_f) * (15 / 360)
    
    dias_vac_tomados = Vacaciones.objects.filter(idcontrato=contrato.idcontrato).aggregate(total=Sum('diasvac'))['total'] or 0
    dias_vacaciones = round(dias_vac_generados - (dias_vac_tomados or 0) , 2)

    
    # Componentes de liquidación
    prima = calcular_prima(int(dias_efectivos_prima), base_prima)
    cesantias = calcular_cesantias(int(dias_efectivos_cesantias), base_cesantias)
    vacaciones = calcular_vacaciones(dias_vacaciones, base_vacaciones)
    intereses = calcular_intereses_cesantias(int(dias_cesantias_brutos), cesantias)
    indemnizacion = calcular_indemnizacion(salario, dias_trabajados, reason ,fecha_fin)

    if es_integral:
        base_prima = base_cesantias = 0
        prima = cesantias = intereses = 0

    total_liquidacion = prima + cesantias + vacaciones + intereses + indemnizacion
    
    data = {
        'dias_trabajados': safe_value(dias_trabajados),
        'dias_prima': safe_value(dias_efectivos_prima),
        'dias_cesantias': safe_value(dias_efectivos_cesantias),
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
        'inicio_contrato': fecha_inicio or "", 
        'fin_contrato': fecha_fin or "",
        # Días susp. vacaciones = suma nómina suspcontrato en todo el contrato hasta retiro
        # (misma magnitud que descuenta en el cálculo de días de vacaciones).
        'dias_susp_vac': safe_value(acum_susp_contrato_f),
        'dias_susp_ces': dias_susp_ces,
        'dias_brutos_cesantias': safe_value(dias_cesantias_brutos),
    }

    return data 

def depurar_suspension_contrato(contrato, suspensiones_qs=None):
    """
    Depura los registros de suspensión de contrato (familia indicador suspcontrato) de un contrato.
    Retorna total de días y detalle de cada nómina involucrada.
    """
    if suspensiones_qs is None:
        suspensiones_qs = Conceptosdenomina.objects.filter(
            indicador__nombre='suspcontrato',
            id_empresa=contrato.id_empresa,
        )
    registros = Nomina.objects.filter(
        idcontrato=contrato.idcontrato,
        estadonomina=2,
        idconcepto__id_empresa=contrato.id_empresa,
        idconcepto__in=suspensiones_qs,
    )

    resultados = []
    total_dias_susp = 0

    for r in registros:
        dias = r.cantidad or 0
        total_dias_susp += dias

        resultados.append({
            "nomina_id": r.idnomina.idnomina,
            "concepto": r.idconcepto.nombreconcepto,
            "codigo": r.idconcepto.codigo,
            "dias_susp": dias,
            "valor": r.valor
        })

    return {
        "total_dias_susp": total_dias_susp,
        "detalle": resultados
    }

def depurar_vacaciones(contrato):
    """
    Depura los registros de vacaciones directamente desde Vacaciones,
    comparando con la cantidad y valor en Nomina.

    Lógica:
        - Solo se cuentan las vacaciones donde:
            Nomina.cantidad == Vacaciones.diascalendario
            Nomina.valor == Vacaciones.pagovac
        - Si coincide, se toma diasvac
    """
    registros_nomina = Nomina.objects.filter(
        idcontrato=contrato.idcontrato,
        estadonomina=2,
        idconcepto__id_empresa=contrato.id_empresa,
        idconcepto__indicador__nombre='Vacaciones_Ausent'
    )

    resultados = []
    total_dias_vac = 0

    # Traemos todas las vacaciones del contrato
    vacaciones = Vacaciones.objects.filter(idcontrato_id=contrato.idcontrato)

    for r in registros_nomina:
        # Buscamos coincidencias directas
        vac_coincidente = next(
            (v for v in vacaciones if (r.cantidad == v.diascalendario and r.valor == v.pagovac)),
            None
        )

        
        dias_a_contar = vac_coincidente.diasvac if vac_coincidente else 0
        total_dias_vac += dias_a_contar

    return total_dias_vac

