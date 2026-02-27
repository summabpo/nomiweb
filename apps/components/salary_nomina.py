from apps.common.models import Crearnomina , HistoricoNomina ,NominaComprobantes, NovSalarios , Empresa , Anos , Nomina , Contratos
from decimal import Decimal



def salary_nomina_update(contrato, fecha_inicio, fecha_fin):

    estructura = []

    salario_actual = contrato.salario

    print("\n========= ANALISIS CAMBIO SALARIAL =========")
    print("Periodo:", fecha_inicio, "->", fecha_fin)
    print("Salario actual contrato:", salario_actual)

    cambio = NovSalarios.objects.filter(
        idcontrato=contrato,
        fechanuevosalario__gt=fecha_inicio,
        fechanuevosalario__lte=fecha_fin
    ).order_by('fechanuevosalario').first()

    # 🔹 Caso 1: No hay cambio dentro del periodo
    if not cambio:
        dias_totales = (fecha_fin - fecha_inicio).days + 1

        estructura.append({
            "dias": dias_totales,
            "salario_mensual": salario_actual,
            "salario_dia": salario_actual / Decimal(30)
        })


        return estructura

    # 🔹 Caso 2: Sí hubo cambio dentro del periodo

    salario_anterior = cambio.salarioactual
    fecha_cambio = cambio.fechanuevosalario


    dias_anteriores = (fecha_cambio - fecha_inicio).days
    dias_nuevos = (fecha_fin - fecha_cambio).days + 1



    # Tramo 1
    if dias_anteriores > 0:
        estructura.append({
            "dias": dias_anteriores,
            "salario_mensual": salario_anterior,
            "salario_dia": salario_anterior / 30
        })

    # Tramo 2
    estructura.append({
        "dias": dias_nuevos,
        "salario_mensual": salario_actual,
        "salario_dia": salario_actual /30
    })

    print("Estructura generada:", estructura)
    print("============================================\n")

    return estructura











