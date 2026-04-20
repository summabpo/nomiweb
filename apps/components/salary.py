from datetime import datetime , date
from apps.common.models import NovSalarios 


def salario_mes(contrato, mes, ano):
    fecha_consulta = date(ano, mes, 1)

    cambios = (
        NovSalarios.objects
        .filter(idcontrato=contrato)
        .order_by('-fechanuevosalario', '-idcambiosalario')  # 🔥 clave
    )

    for cambio in cambios:
        if fecha_consulta >= cambio.fechanuevosalario:
            return (
                cambio.nuevosalario
                or cambio.salarioactual
                or contrato.salario
            )

    primer_cambio = cambios.last()

    if primer_cambio and primer_cambio.salarioactual:
        return primer_cambio.salarioactual

    return contrato.salario