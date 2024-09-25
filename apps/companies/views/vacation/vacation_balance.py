from django.shortcuts import render
from apps.companies.models import Contratos, Vacaciones, Conceptosfijos
from django.db.models import Q, Sum
from django.utils import timezone
from apps.components.utils import calcular_dias_360
from datetime import datetime


def calcular_vacaciones(contrato, concepto,fecha_actual):
    # Calcular las vacaciones disponibles
    total_vac_disf = Vacaciones.objects.filter(
        idcontrato=contrato.idcontrato
    ).filter(Q(tipovac='1') | Q(tipovac='2')).aggregate(Sum('diasvac'))['diasvac__sum'] or 0

    # Fecha actual y fecha inicial
    fecha_actual = fecha_actual
    fecha_inicial = contrato.fechainiciocontrato

    total_vac = (calcular_dias_360(fecha_inicial.strftime("%Y-%m-%d"), fecha_actual.strftime("%Y-%m-%d"))) * (concepto/100)
    saldo = total_vac - total_vac_disf

    return {
        "total_vac_disf": round(total_vac_disf, 2),
        "total_vac": round(total_vac, 2),
        "saldo": round(saldo, 2)
    }


def vacation_balance(request):
    acumulados= {} 
    
    concepto = Conceptosfijos.objects.filter(idfijo=9).values_list('valorfijo', flat=True).first()

    valor_fijo = float(concepto)
    
    fecha_param = request.GET.get('fecha')
    fecha_actual = timezone.now().date() if fecha_param is None else datetime.strptime(fecha_param, "%Y-%m-%d").date()

    if fecha_param :
        contratos_empleados = Contratos.objects.prefetch_related('idempleado') \
            .filter(estadocontrato=1) \
            .values('idempleado__docidentidad', 'idempleado__sapellido', 'idempleado__papellido',
                    'idempleado__pnombre', 'idempleado__snombre', 'idempleado__idempleado',
                    'idcontrato', 'fechainiciocontrato','salario').order_by('idempleado__papellido')

        acumulados = {
            data['idcontrato']: {
                'contrato': data['idcontrato'],
                'documento': data['idempleado__docidentidad'],
                'empleado': f"{data['idempleado__papellido']} {data['idempleado__sapellido']} {data['idempleado__pnombre']} {data['idempleado__snombre']}",
                'fechacontrato': data['fechainiciocontrato'],
                'salario': data['salario'],
                'parcial': round(float(data['salario']) / 30, 2),
            }
            for data in contratos_empleados
        }


        for contrato_id in acumulados.keys():
            contrato = Contratos.objects.get(idcontrato=contrato_id)
            vacaciones_data = calcular_vacaciones(contrato, valor_fijo ,fecha_actual)

            # Agrega la información de vacaciones al diccionario acumulados
            acumulados[contrato_id].update(vacaciones_data)

    context = {
        'contratos_empleados': list(acumulados.values()),
    }

    return render(request, './companies/vacation_balance.html', context)