from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.components.decorators import role_required
from apps.common.models import Crearnomina, Nomina
from django.http import HttpResponse
from openpyxl import Workbook

# -------------------------
# CONFIG
# -------------------------

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

# -------------------------
# VIEW PRINCIPAL
# -------------------------

@login_required
@role_required('accountant')
def PayrollAuditExcel(request, payroll_id):

    name_nomina = Crearnomina.objects.get(idnomina=payroll_id).nombrenomina
    name_nomina = name_nomina.replace(" - ", "_")
    name = f"auditoria_{name_nomina}.xlsx"

    wb = Workbook()
    wb.remove(wb.active)

    empleados = get_nomina_data(payroll_id)

    build_nomina_sheet(wb, empleados, payroll_id)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{name}"'

    wb.save(response)
    return response

# -------------------------
# DATA BASE
# -------------------------

def get_nomina_data(payroll_id):
    return Nomina.objects.select_related('idcontrato').filter(
        idnomina=payroll_id,
        estadonomina=1
    ).values(
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
    ).distinct()

# -------------------------
# CONCEPTOS
# -------------------------

def get_special_concepts_present(payroll_id):
    return list(
        Nomina.objects.filter(
            idnomina_id=payroll_id,
            estadonomina=1,
            idconcepto__codigo__in=SPECIAL_CONCEPTS.keys()
        ).values_list('idconcepto__codigo', flat=True).distinct()
    )


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

    return sorted(list(conceptos), key=lambda x: x['idconcepto__codigo'])


def get_conceptos_por_empleado(emp, payroll_id):

    movimientos = Nomina.objects.filter(
        idcontrato_id=emp['idcontrato'],
        idnomina_id=payroll_id,
    ).values(
        'idconcepto__codigo',
        'valor',
        'cantidad'
    )

    data = {}
    for mov in movimientos:
        data[mov['idconcepto__codigo']] = {
            'valor': mov['valor'],
            'cantidad': mov['cantidad']
        }

    return data

# -------------------------
# HELPERS BASE
# -------------------------

def get_sueldo(emp, payroll_id):

    tipo_salario = emp.get('idcontrato__tiposalario__idtiposalario')
    tipo_contrato = emp.get('idcontrato__tipocontrato__idtipocontrato')

    if tipo_salario == 2:
        codigo_aux = '4'
    elif tipo_contrato == 6:
        codigo_aux = '34'
    else:
        codigo_aux = '1'

    salario_n = Nomina.objects.filter(
        idcontrato_id=emp['idcontrato'],
        idnomina_id=payroll_id,
        idconcepto__codigo=codigo_aux,
        estadonomina=1
    ).first()

    if not salario_n:
        return 0, 0

    return salario_n.valor or 0, salario_n.cantidad or 0


def get_transporte(emp, payroll_id):
    obj = Nomina.objects.filter(
        idcontrato_id=emp['idcontrato'],
        idnomina_id=payroll_id,
        idconcepto__codigo=2,
        estadonomina=1
    ).first()

    return obj.valor if obj else 0


def get_eps_pension(emp, payroll_id):

    eps = Nomina.objects.filter(
        idcontrato_id=emp['idcontrato'],
        idnomina_id=payroll_id,
        idconcepto__codigo=60
    ).first()

    pension = Nomina.objects.filter(
        idcontrato_id=emp['idcontrato'],
        idnomina_id=payroll_id,
        idconcepto__codigo=70
    ).first()

    return (eps.valor if eps else 0), (pension.valor if pension else 0)

# -------------------------
# EXCEL
# -------------------------

def build_nomina_sheet(workbook, empleados, payroll_id):

    sheet = workbook.create_sheet(title='Nomina')

    conceptos = get_conceptos_nomina(payroll_id)
    specials_present = get_special_concepts_present(payroll_id)

    headers = [
        'Empleado', 'Documento',
        'Salario', 'Cantidad', 'Valor',
        'Transporte', 'EPS', 'Pension'
    ]

    # especiales dinámicos (solo si existen)
    for codigo in specials_present:
        nombre = SPECIAL_CONCEPTS[codigo]
        headers.append(f"{nombre} Cantidad")
        headers.append(f"{nombre} Valor")

    # dinámicos
    for c in conceptos:
        headers.append(c['idconcepto__nombreconcepto'])

    headers.append('Total a pagar')

    sheet.append(headers)

    # filas
    for emp in empleados:

        nombre = f"{emp['idcontrato__idempleado__pnombre']} {emp['idcontrato__idempleado__snombre']} {emp['idcontrato__idempleado__papellido']} {emp['idcontrato__idempleado__sapellido']}"

        salario, cantidad = get_sueldo(emp, payroll_id)
        trans = get_transporte(emp, payroll_id)
        eps, pension = get_eps_pension(emp, payroll_id)

        conceptos_emp = get_conceptos_por_empleado(emp, payroll_id)

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

        total += salario or 0
        total += trans or 0
        total += eps or 0
        total += pension or 0

        # especiales SOLO existentes
        for codigo in specials_present:
            data = conceptos_emp.get(codigo, {})
            cant = data.get('cantidad', 0)
            val = data.get('valor', 0)

            row.append(cant)
            row.append(val)

            total += val or 0

        # dinámicos
        for c in conceptos:
            valor = conceptos_emp.get(c['idconcepto__codigo'], {}).get('valor', 0)
            row.append(valor)

            total += valor or 0

        row.append(total)

        sheet.append(row)