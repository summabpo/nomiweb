from datetime import datetime , date
from apps.common.models import NovSalarios 


def salario_mes(contrato, mes, ano):
    """
    Devuelve el salario vigente para un contrato en un mes y año específicos,
    considerando los cambios de salario.
    """
    # Salario por defecto
    salario = contrato.salario

    # Fecha del mes que queremos consultar
    fecha_consulta = date(ano, mes, 1)

    # Último cambio de salario registrado para este contrato
    cambio = NovSalarios.objects.filter(
        idcontrato=contrato
    ).order_by('-fechanuevosalario').first()  # último cambio



    if cambio:
        # Si la fecha de consulta es **antes** del cambio → salarioactual
        if fecha_consulta < cambio.fechanuevosalario:
            if cambio.salarioactual is not None:
                salario = cambio.salarioactual
                
        else:
            # Si es igual o después → nuevosalario
            if cambio.nuevosalario is not None:
                salario = cambio.nuevosalario
    
    return salario