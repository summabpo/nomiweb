from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina , Tipodenomina , Liquidacion , EditHistory , Conceptosfijos , Salariominimoanual,Conceptosdenomina , Empresa , Anos , Nomina , Contratos
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

## FIJAS AUDIT
from django.http import HttpResponse
from openpyxl import Workbook

## conceptos especiales
SPECIAL_DAY_CODES = [25, 26, 27, 28, 30, 86, 24, 32, 824, 31, 83, 82]
EXCLUDE_CODES = [1, 2, 4, 34, 60, 70] + SPECIAL_DAY_CODES

SPECIAL_CONCEPTS = {
    25: 'Incapacidad E.Gral',
    26: 'Incapacidad 2 dias E.Gral',
    27: 'Incapacidad ARL',
    28: 'Incapacidad ARL 1 dia',
    30: 'Suspension - Ingreso',
    86: 'Suspension - Deducción',
    24: 'Vacaciones',
    32: 'Vacaciones Compensadas',
    824: 'Vacaciones Consolidadas',
    31: 'Licencia NO Remunerada - Ingreso',
    83: 'Licencia NO Remunerada - Deducción',
    82: 'Licencia Remunerada',
    
}







@login_required
@role_required('accountant')
def PayrollAuditExcel(request, payroll_id):
    name_nomina  =  Crearnomina.objects.get(idnomina=payroll_id).nombrenomina
    name_nomina = name_nomina.replace(" - ", "_")
    name = f"auditoria_{name_nomina}.xlsx"
    # Crear workbook
    wb = Workbook()

    # Eliminar hoja por defecto
    default_sheet = wb.active
    wb.remove(default_sheet)

    # Obtener data
    empleados = get_nomina_data(payroll_id)

    # Crear hojas (pasando data)
    build_nomina_sheet(wb, empleados,payroll_id)

    # (luego agregas estas cuando tengas data)
    # build_incapacidades_sheet(wb, data)
    # build_suspensiones_sheet(wb, data)
    # build_vacaciones_sheet(wb, data)

    # Response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{name}"'

    wb.save(response)
    return response


def get_nomina_data(payroll_id):
    
    empleados_raw = Nomina.objects \
        .select_related('idcontrato') \
        .filter(idnomina=payroll_id, estadonomina=1) \
        .values(
            'idcontrato__idempleado__docidentidad',
            'idcontrato__idempleado__papellido',
            'idcontrato__idempleado__sapellido',
            'idcontrato__idempleado__pnombre',
            'idcontrato__idempleado__snombre',
            'idcontrato__salario',
            'idcontrato__idempleado__idempleado',
            'idcontrato__tiposalario__idtiposalario',
            'idcontrato__tipocontrato__idtipocontrato',
            'idcontrato',
        ) \
        .distinct()
        
    return empleados_raw


def build_nomina_sheet(workbook, empleados, payroll_id):
    sheet = workbook.create_sheet(title='Nomina')

    # conceptos dinámicos
    conceptos = get_conceptos_nomina(payroll_id)

    # headers base (fijos)
    headers = [
    'Empleado', 'Documento',
        'Salario', 'Cantidad', 'Valor',
        'Transporte', 'EPS', 'Pension'
    ]

    # agregar especiales (doble columna)
    for codigo, nombre in SPECIAL_CONCEPTS.items():
        headers.append(f"{nombre} Cantidad")
        headers.append(f"{nombre} Valor")

    # agregar conceptos dinámicos
    for c in conceptos:
        headers.append(c['idconcepto__nombreconcepto'])

    # total
    headers.append('Total a pagar')

    sheet.append(headers)

    # filas
    for emp in empleados:

        nombre = f"{emp['idcontrato__idempleado__pnombre']} {emp['idcontrato__idempleado__snombre']} {emp['idcontrato__idempleado__papellido']} {emp['idcontrato__idempleado__sapellido']}"

        salario, cantidad = get_sueldo(emp, payroll_id)
        trans = get_transporte(emp, payroll_id)
        eps, pension = get_eps_pension(emp, payroll_id)

        conceptos_emp = get_conceptos_por_empleado(emp, payroll_id)

        # acumulador
        total = 0

        row = [
            nombre,
            emp['idcontrato__idempleado__docidentidad'],
            emp['idcontrato__salario'],
            cantidad,
            salario,
            trans,
            eps,
            pension,
        ]

        # sumar base
        total += salario or 0
        total += trans or 0
        total += eps or 0
        total += pension or 0

        # especiales
        for codigo in SPECIAL_CONCEPTS.keys():
            cant, val = get_concepto_cantidad_valor(emp, payroll_id, codigo)
            row.append(cant)
            row.append(val)

            total += val or 0   # SOLO valor

        # dinámicos
        for c in conceptos:
            valor = conceptos_emp.get(c['idconcepto__codigo'], 0)
            row.append(valor)

            total += valor or 0

        # agregar total al final
        row.append(total)

        sheet.append(row)


def get_conceptos_nomina(payroll_id):


    conceptos = Nomina.objects.filter(
        idnomina_id=payroll_id,
        estadonomina=1
    ).exclude(
        idconcepto__codigo__in=EXCLUDE_CODES
    ).values(
        'idconcepto__codigo',
        'idconcepto__nombreconcepto'
    ).distinct()

    # lista ordenada
    return sorted(list(conceptos), key=lambda x: x['idconcepto__codigo'])


def get_conceptos_por_empleado(emp, payroll_id):
    
    movimientos = Nomina.objects.filter(
        idcontrato_id=emp['idcontrato'],
        idnomina_id=payroll_id,
    ).values(
        'idconcepto__codigo',
        'valor'
    )

    # diccionario: {codigo: valor}
    data = {}
    for mov in movimientos:
        data[mov['idconcepto__codigo']] = mov['valor']

    return data



def get_sueldo(emp, payroll_id):

    tipo_salario = emp.get('contrato__tiposalario__idtiposalario')
    tipo_contrato = emp.get('contrato__tipocontrato_idtipocontrato')

    if tipo_salario == 2:
        codigo_aux = '4'
    elif tipo_contrato == 6:
        codigo_aux = '34'
    else:
        codigo_aux = '1'

    #  Buscar registro de salario (seguro)
    salario_n = Nomina.objects.filter(
        idcontrato_id=emp['idcontrato'],
        idnomina_id=payroll_id,
        idconcepto__codigo=codigo_aux,
        estadonomina=1
    ).first()

    # Protección
    if not salario_n:
        return 0, 0

    salario = salario_n.valor or 0
    cantidad = salario_n.cantidad or 0

    return salario, cantidad


def get_transporte(emp, payroll_id):
    
    transporte = Nomina.objects.filter(
        idcontrato_id=emp['idcontrato'],
        idnomina_id=payroll_id,
        idconcepto__codigo=2,
        estadonomina=1
    ).first()

    return transporte.valor if transporte else 0


def get_eps_pension(emp, payroll_id):
    eps = 0
    pension = 0

    eps = Nomina.objects.filter(
        idcontrato_id=emp['idcontrato'],
        idnomina_id=payroll_id,
        idconcepto__codigo=60,
    ).first() or 0

    pension = Nomina.objects.filter(
        idcontrato_id=emp['idcontrato'],
        idnomina_id=payroll_id,
        idconcepto__codigo=70,
    ).first() or 0

    return eps.valor if eps else 0 , pension.valor if pension else 0


def get_concepto_cantidad_valor(emp, payroll_id, codigo):

    concepto = Nomina.objects.filter(
        idcontrato_id=emp['idcontrato'],
        idnomina_id=payroll_id,
        idconcepto__codigo=codigo,
        estadonomina=1
    ).first()

    if not concepto:
        return 0, 0

    cantidad = concepto.cantidad or 0
    valor = concepto.valor or 0

    return cantidad, valor


def build_incapacidades_sheet(workbook, payroll_id):
    sheet = workbook.create_sheet(title='Incapacidades')

    headers = [
        'Empleado', 'Tipo', 'Fecha Inicio', 'Fecha Fin', 'Valor'
    ]
    sheet.append(headers)


def build_suspensiones_sheet(workbook, payroll_id):
    sheet = workbook.create_sheet(title='Suspensiones')

    headers = [
        'Empleado', 'Fecha Inicio', 'Fecha Fin', 'Motivo'
    ]
    sheet.append(headers) 


def build_vacaciones_sheet(workbook, payroll_id):
    sheet = workbook.create_sheet(title='Vacaciones')

    headers = [
        'Empleado', 'Fecha Inicio', 'Fecha Fin', 'Días'
    ]
    sheet.append(headers)




