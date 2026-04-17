from struct import pack_into
from traceback import print_tb
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Contratos, Crearnomina , Ingresosyretenciones ,Anos , Nomina
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

@login_required
@role_required('accountant')
def income_withholding_certificate(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    years = Anos.objects.all().order_by('-ano')
    context = {
        'years': years,
    }
    
    # 👇 CAPTURAR GET
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
    years = Anos.objects.all().order_by('-ano')
    context = {
        'years': years,
    }
    if request.method == "POST":
        try:
            anio = request.POST.get('anio')
            
            data = get_contratos_por_anio(anio,idempresa)
            certificado = data_certificate(data, anio , idempresa)
            #print(json.dumps(certificado, indent=4, ensure_ascii=False))
            
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
            pensiones = returne_value_for_family(contrato.idcontrato, anoacumular, 'pensiones') or 0
            aportessalud = returne_value_for_family(contrato.idcontrato, anoacumular, 'aportessalud') or 0
            aportespension = returne_value_for_family(contrato.idcontrato, anoacumular, 'aportespension') or 0
            aportesvoluntarios = returne_value_for_family(contrato.idcontrato, anoacumular, 'aportesvoluntarios') or 0

            cesantias90 = returne_value_for_concepto(contrato.idcontrato, anoacumular,820 ) or 0
            otros_pagos = returne_value_for_family(contrato.idcontrato, anoacumular, 'otrospagos') or 0
            apoyoeconomico = returne_value_for_family(contrato.idcontrato, anoacumular, 'apoyoeconomico') or 0
            
            # 🔹 acumular
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

        # 🔥 cálculo final
        data['totalingresosbrutos'] = (
            data['salarios'] + data['honorarios'] + data['servicios'] + data['comisiones']
        )

        # 🔥 guardar UNA sola vez por empleado
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