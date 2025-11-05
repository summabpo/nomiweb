from datetime import date
from math import ceil
from django.db.models import Sum

# --- Utilidades generales --- #

def dias_360(date1: date, date2: date) -> int:
    """Calcula días entre dos fechas con regla 360."""
    d1 = date1.day
    d2 = date2.day
    m1 = date1.month
    m2 = date2.month
    y1 = date1.year
    y2 = date2.year
    diff = (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1) 
    if d1 == 31:
        diff += 1
    return diff + 1


def dias_360_2(date1: date, date2: date) -> int:
    """Calcula los días entre dos fechas como si todos los meses tuvieran 30 días (regla 30/360)."""
    
    d1 = min(date1.day, 30)
    d2 = date2.day
    
    if date1.day == 31 or (date1.day == 30 and date2.day == 31):
        d2 = 30
    
    m1 = date1.month
    m2 = date2.month
    y1 = date1.year
    y2 = date2.year

    return (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)

# --- Fechas base --- #

def obtener_fecha_cesantias(fecha_inicio, fecha_ano_actual):
    return max(fecha_inicio, date(fecha_ano_actual.year, 1, 1))

def obtener_fecha_prima(fecha_inicio, fecha_fin):
    mitad_ano = date(fecha_fin.year, 6, 30)
    if fecha_inicio < date(fecha_fin.year, 1, 1):
        return date(fecha_fin.year, 7, 1) if fecha_fin > mitad_ano else date(fecha_fin.year, 1, 1)
    else:
        if fecha_fin > mitad_ano and fecha_inicio > mitad_ano:
            return fecha_inicio
        elif fecha_fin > mitad_ano and fecha_inicio < mitad_ano:
            return date(fecha_fin.year, 7, 1)
        else:
            return fecha_inicio

# --- Cálculos acumulados --- #

def obtener_acumulado_nomina(queryset, campo="valor"):
    return queryset.aggregate(total=Sum(campo))["total"] or 0

def acumular_por_mes(model, conceptos_qs, id_contrato, ano, mes_inicio, mes_fin, campo="valor"):
    total = 0
    for mes in range(mes_inicio, mes_fin + 1):
        qset = model.objects.filter(
            idcontrato=id_contrato,
            idnomina__mesacumular=mes,
            idnomina__anoacumular=ano,
            estadonomina=2,
            idconcepto__in=conceptos_qs
        )
        total += obtener_acumulado_nomina(qset, campo)
        
        
    return total

# --- Cálculo de bases --- #

def calcular_base_promedio(acumulado: float, dias: int, salario: float, transporte: float = 0) -> int:
    if dias <= 0:
        return ceil(salario + transporte)
    promedio = acumulado / dias * 30
    return ceil(promedio + salario + transporte)



def calcular_base_vacaciones(acum_recargos: float, dias_cesantias: int, salario: float) -> int:
    if dias_cesantias <= 0:
        return ceil(salario)
    return ceil((acum_recargos / dias_cesantias * 30) + salario)

# --- Cálculo de componentes de liquidación --- #

def calcular_intereses_cesantias(dias_cesantias: int, cesantias: float) -> int:
    return ceil(dias_cesantias * (12 / 100) / 360 * cesantias)

def calcular_prima(dias_prima: int, base_prima: float) -> int:
    return ceil(dias_prima / 360 * base_prima)

def calcular_cesantias(dias_cesantias: int, base_cesantias: float) -> int:
    return ceil(base_cesantias * dias_cesantias / 360)

def calcular_vacaciones(dias_vacaciones: float, base_vacaciones: float) -> int:
    return ceil(base_vacaciones * dias_vacaciones / 30)

def calcular_indemnizacion(salario: float, dias_trabajados: int, motivo_retiro: str) -> float:
    if motivo_retiro != 'Despido sin justa causa':
        return 0
    if dias_trabajados <= 360:
        return salario
    return salario + (((dias_trabajados - 360) / 360) * 20) * (salario / 30)


def safe_value(value):
    return value if value not in [None, ''] else 0