
from apps.common.models import Tipodenomina , Conceptosdenomina ,Nomina, Crearnomina , Contratos , Anos, Liquidacion , Salariominimoanual , Nomina,Vacaciones
from apps.payroll.views.settlements.liquidacion_utils import *
from django.db.models import Sum
from datetime import datetime , date
from django.db.models import Q

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
        
    }
    if not (contract_id and end_date and reason):
        return data 

    try:
        contrato = Contratos.objects.get(idcontrato=contract_id)
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


    if contrato.tipocontrato_id == 6:
        data['inicio_contrato'] = fecha_inicio
        data['salario'] = salario
        data['dias_trabajados'] = dias_trabajados
        data['fin_contrato'] = fecha_fin
        return data 
    
    
    salario_minimo = salario_min_obj.salariominimo
    aux_transporte = 0 if salario > (2 * salario_minimo) else salario_min_obj.auxtransporte

    # Conceptos
    extras_y_comisiones_qs = Conceptosdenomina.objects.filter(Q(indicador__nombre='extras') | Q(indicador__nombre='comisiones') ,id_empresa = contrato.id_empresa)
    suspensiones_qs = Conceptosdenomina.objects.filter( indicador__nombre = 'suspcontrato',id_empresa = contrato.id_empresa)
    recargos_qs = Conceptosdenomina.objects.filter(indicador__nombre = 'basevacaciones',id_empresa = contrato.id_empresa)
    
    # Acumulados

    acum_cesantias = acumular_por_mes(Nomina,extras_y_comisiones_qs,contrato.idcontrato,fecha_cesantias.year,fecha_cesantias.month,fecha_fin.year,fecha_fin.month)
    acum_prima = acumular_por_mes(Nomina,extras_y_comisiones_qs,contrato.idcontrato,fecha_prima.year,fecha_prima.month,fecha_fin.year,fecha_fin.month)
    acum_susp = acumular_por_mes(Nomina,suspensiones_qs,contrato.idcontrato,fecha_cesantias.year,fecha_cesantias.month,fecha_fin.year,fecha_fin.month,campo="cantidad")
    acum_recargos = acumular_por_mes(Nomina,recargos_qs,contrato.idcontrato,fecha_cesantias.year,fecha_cesantias.month,fecha_fin.year,fecha_fin.month)
    
    #acum_susp = acum_prima = acum_cesantias = 0 



    # Días efectivos
    dias_efectivos_cesantias = dias_cesantias - acum_susp
    dias_efectivos_prima = dias_prima

    # Bases
    base_cesantias = calcular_base_promedio(acum_cesantias, dias_efectivos_cesantias, salario, aux_transporte)
    base_prima = calcular_base_promedio(acum_prima, dias_efectivos_prima, salario, aux_transporte)
    base_vacaciones = calcular_base_vacaciones(acum_recargos, dias_trabajados, salario)

    # Vacaciones
    dias_susp_ces = Nomina.objects.filter(
        idcontrato=contrato.idcontrato,
        estadonomina=2,
        idconcepto__id_empresa = contrato.id_empresa ,
        idconcepto__indicador__nombre='suspcontrato'
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    dias_vac = Nomina.objects.filter(
        idcontrato=contrato.idcontrato,
        estadonomina=2,
        idconcepto__id_empresa = contrato.id_empresa ,
        idnomina__tiponomina__idtiponomina__in=(1, 2, 11),
        idconcepto__indicador__nombre='Vacaciones_Ausent'
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    dias_trabajados = float(dias_trabajados or 0)
    dias_vac = float(dias_vac or 0)
    acum_susp = float(acum_susp or 0)

    dias_vac_generados = (dias_trabajados - dias_vac - acum_susp) * (15 / 360)

    #dias_vac_generados = (dias_trabajados - (dias_vac or 0) - int(acum_susp or 0)) * (15 / 360) 
    
    dias_vac_tomados = Vacaciones.objects.filter(idcontrato=contrato.idcontrato).aggregate(total=Sum('diasvac'))['total'] or 0
    dias_vacaciones = round(dias_vac_generados - (dias_vac_tomados or 0) , 2)

    
    # Componentes de liquidación
    prima = calcular_prima(int(dias_efectivos_prima), base_prima)
    cesantias = calcular_cesantias(int(dias_efectivos_cesantias), base_cesantias)
    vacaciones = calcular_vacaciones(dias_vacaciones, base_vacaciones)
    intereses = calcular_intereses_cesantias(dias_cesantias, cesantias)
    indemnizacion = calcular_indemnizacion(salario, dias_trabajados, reason)

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
        'dias_susp_vac':dias_vac,
        'dias_susp_ces':dias_susp_ces,
    }

    return data 