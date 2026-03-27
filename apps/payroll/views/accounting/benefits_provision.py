from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Tiempos , Crearnomina , Contratos ,Nomina,Conceptosdenomina, Empresa ,Conceptosfijos ,TiemposTotales ,Sedes, Costos, Subcostos, Empresa
from apps.payroll.forms.filter_basic_form import FilterBasicForm
from django.db.models import Q
from math import ceil
from decimal import Decimal, ROUND_HALF_UP
from apps.payroll.views.settlements.liquidacion_utils import *
import calendar
from apps.components.salary import salario_mes

MESES_MAP = {
    'ENERO': 1, 'FEBRERO': 2, 'MARZO': 3, 'ABRIL': 4, 'MAYO': 5, 'JUNIO': 6,
    'JULIO': 7, 'AGOSTO': 8, 'SEPTIEMBRE': 9, 'OCTUBRE': 10, 'NOVIEMBRE': 11, 'DICIEMBRE': 12,
}


@login_required
@role_required('accountant')
def employee_benefits_provision(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    form = FilterBasicForm()
    empleados = []

    def clean_value(value):
        if isinstance(value, str) and value.strip().lower() in ["no data", "sin dato", "n/a", "none", "ninguno"]:
            return ""
        return value
    
    def to_decimal(value, default):
        """
        Convierte cualquier valor a Decimal de forma segura.
        - Soporta None
        - Soporta strings con coma (ej: '4,16')
        - Evita errores de precisión con float
        """
        try:
            if value is None:
                return Decimal(default)
            return Decimal(str(value).replace(',', '.'))
        except:
            return Decimal(default)

    if request.method == 'POST':
        form = FilterBasicForm(request.POST)
        if form.is_valid():
            mst_init = form.cleaned_data['mst_init']
            year_init = int(form.cleaned_data['year_init'])

            # 🔹 Traer conceptos fijos UNA SOLA VEZ
            conceptos = Conceptosfijos.objects.filter(
                conceptofijo__in=['CESANTIAS', 'Intereses de Cesantias', 'Vacaciones']
            ).values_list('conceptofijo', 'valorfijo')
            conceptos_dict = {c[0]: c[1] for c in conceptos}

            # =========================
            # PROVISIONES MENSUALES (%)
            # =========================

            # Cesantías:
            # Legalmente equivalen a 1 salario por año (100%)
            # → Provisión mensual = 100% / 12 = 8.3333%
            cc = to_decimal(conceptos_dict.get('CESANTIAS'), '8.3333')

            # Prima de servicios:
            # También equivale a 1 salario anual (100%)
            # → Provisión mensual = 8.3333%
            cp = to_decimal(conceptos_dict.get('Prima de Servicios'), '8.3333')

            # Intereses de cesantías:
            # 12% anual sobre cesantías
            # → Provisión mensual = 12% / 12 = 1%
            icc = to_decimal(conceptos_dict.get('Intereses de Cesantias'), '1')

            # Vacaciones:
            # Corresponden a 15 días por año
            # → Factor exacto: 15 / 360 = 0.041666...
            # → En porcentaje ≈ 4.1667%
            vac = to_decimal(conceptos_dict.get('Vacaciones'), '4.1667')

            # 🔹 Contratos activos de la empresa  , idcontrato = 8135
            contratos_empleados = (
                Contratos.objects
                .filter(estadocontrato=1, id_empresa=idempresa  )
                .select_related('idempleado', 'cargo', 'idcosto', 'tiposalario')
                .order_by('idempleado__papellido')
                .values(
                    'idempleado__docidentidad', 'idempleado__papellido', 'idempleado__sapellido',
                    'idempleado__pnombre', 'idempleado__snombre', 'fechainiciocontrato',
                    'cargo__nombrecargo', 'salario', 'idcosto__idcosto', 'idempleado__idempleado',
                    'idcontrato', 'id_empresa', 'tiposalario__idtiposalario','tipocontrato__idtipocontrato'
                )
            )

            for contrato in contratos_empleados:
                contract = Contratos.objects.get(idcontrato = contrato['idcontrato'])
                salario = salario_mes(contract,MESES_MAP[mst_init],year_init)

                # 🔹 Base mensual según nómina

                base_c = base_cesantias(contrato, year_init, mst_init)
                base_p = base_prima(contrato, year_init, mst_init)

                if base_c < salario:
                    base_c = salario
                
                if base_p < salario:
                    base_p = salario

                # bb = base_cesantias_debug(contrato, year_init, mst_init)

                if contrato['tiposalario__idtiposalario'] == 2 or contrato['tipocontrato__idtipocontrato'] == 6:  # Por ejemplo: contratos sin prestaciones
                    base_p = cesantias = intereses = prima = 0

                else:
                    # 🔹 Cálculos provisionales mensuales
                    cesantias = (base_c * (cc/Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) # 1 mes / 12 meses
                    intereses = (base_c * (icc / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)  # 12% anual proporcional mensual
                    prima = (base_p * (cp / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) # 1 mes / 12 meses
                    
                    
                vacaciones = (salario * (vac / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)  # 1/12 del salario mensual

                total = cesantias + intereses + prima + vacaciones

                nombre = " ".join(filter(None, [
                    clean_value(contrato.get('idempleado__papellido')),
                    clean_value(contrato.get('idempleado__sapellido')),
                    clean_value(contrato.get('idempleado__pnombre')),
                    clean_value(contrato.get('idempleado__snombre')),
                ]))

                
                empleados.append({
                    'documento': clean_value(contrato.get('idempleado__docidentidad')),
                    'nombre': nombre,
                    'fechainiciocontrato': contrato.get('fechainiciocontrato'),
                    'cargo': clean_value(contrato.get('cargo__nombrecargo')),
                    'salario': salario,
                    'base': base_p,
                    'cesantias': float(cesantias),
                    'intereses': float(intereses),
                    'prima': float(prima),
                    'vacaciones': float(vacaciones),
                    'total': float(total),
                    'centrocostos': clean_value(contrato.get('idcosto__idcosto')),
                    'idcontrato': contrato.get('idcontrato'),
                })

    return render(request, './payroll/employee_benefits_provision.html', {'empleados': empleados, 'form': form})






def base_cesantias(contrato, year, mes):
    return Nomina.objects.filter(
        idcontrato=contrato['idcontrato'],
        estadonomina=2,
        idnomina__mesacumular=mes,
        idnomina__anoacumular__ano=year,
        idconcepto__indicador__nombre='baseprima'
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')


def base_cesantias_debug(contrato, year, mes):
    queryset = Nomina.objects.filter(
        idcontrato=contrato['idcontrato'],
        estadonomina=2,
        idnomina__mesacumular=mes,
        idnomina__anoacumular__ano=year,
        idconcepto__indicador__nombre='baseprima'
    )

    # 🔍 Ver cada registro individual
    detalles = queryset.values(
        'idconcepto__nombreconcepto'
    ).annotate(
        total=Sum('valor')
    )

    print("=== DETALLE BASE CESANTÍAS ===")
    for item in detalles:
        print(f"Concepto: {item['idconcepto__nombreconcepto']} | Valor: {item['total']}")

    # 🔢 Total general
    total = queryset.aggregate(total=Sum('valor'))['total'] or Decimal('0')

    print(f"TOTAL BASE CESANTÍAS: {total}")

    return total

def base_prima(contrato, year, mes):
    return Nomina.objects.filter(
        idcontrato=contrato['idcontrato'],
        estadonomina=2,
        idnomina__mesacumular=mes,
        idnomina__anoacumular__ano=year,
        idconcepto__indicador__nombre='baseprima'
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')


def base_vacaciones(contrato, year, mes):
    return Nomina.objects.filter(
        idcontrato=contrato['idcontrato'],
        estadonomina=2,
        idnomina__mesacumular=mes,
        idnomina__anoacumular__ano=year,
        idconcepto__indicador__nombre='basevacaciones'
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')




