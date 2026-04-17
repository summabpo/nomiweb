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
        anio = request.POST.get('anio')
        print('------------------ empresa--------------')
        print(idempresa)
        print('--------------------------------')
        data = get_contratos_por_anio(anio,idempresa)
        data_certificate(data, anio)
        

    return render(request, 'payroll/partials/generate_certificate.html', context)




def data_certificate(data_contratos, anoacumular):



    data = {
        'salarios':0 ,
        'honorarios' : 0 ,
        'servicios' :0,
        'comisiones' :0,
        'prestacionessociales' :0,
        'viaticos' :0,
        'gastosderepresentacion' :0,
        'compensacioncta' :0,
        'cesantiasintereses' :0,
        'pensiones' :0,
        'totalingresosbrutos' :0,
        'aportessalud' :0,
        'aportespension' :0,
        'aportesvoluntarios' :0,
        'aportesafc' :0,
        'retefuente' :0,
        'anoacumular' : 0,
        'idempleado' : 0,  
        'otrospagos' : 0 ,
        'fondocesantias' : 0 ,
        'excesoalim' : 0 ,
        'cesantias90' : 0 ,
        'apoyoeconomico' : 0 ,
        'aportesavc' : 0 ,
        'ingresolaboralpromedio' : 0 ,
        'id_empresa' : 0,
    }

    
    for cedula, contratos in data_contratos.items():
        salarios = 0
        for contrato in contratos:
            salarios += returne_value_for_family(contrato.idcontrato, anoacumular, 'basesegsocial')
        
        print('--------------------------------')
        print(salarios)
        print('--------------------------------')




    return data


def returne_value_for_family(idcontrato , anoacumular , familia):
    total = 0
    print('--------------------------------')
    print(idcontrato)
    print(anoacumular)
    print(familia)
    print('--------------------------------')

    data = Nomina.objects.filter(
        idnomina__anoacumular__ano=int(2025),
        idcontrato_id=int(idcontrato),
    )

    for item in data:
        print(item.idconcepto.nombreconcepto)
        print(item.valor)
        print('--------------------------------')   
        total += item.valor

    return total or 0


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