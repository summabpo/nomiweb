
from cmd import IDENTCHARS
import decimal
import re
from traceback import print_exception
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Tipodenomina , Conceptosdenomina,Conceptosfijos ,Nomina, Crearnomina , Contratos , Anos, Liquidacion , Salariominimoanual , Nomina,Vacaciones
from datetime import datetime, timedelta ,date
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Q
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Submit
from apps.common.models import Contratos , Crearnomina
from django.urls import reverse
import calendar
from django.db.models.functions import ExtractMonth
from django.db.models import Sum
from apps.components.salary import salario_mes
import json


MESES_MAP = {
    'ENERO': 1, 'FEBRERO': 2, 'MARZO': 3, 'ABRIL': 4, 'MAYO': 5, 'JUNIO': 6,
    'JULIO': 7, 'AGOSTO': 8, 'SEPTIEMBRE': 9, 'OCTUBRE': 10, 'NOVIEMBRE': 11, 'DICIEMBRE': 12,
}

MESES_MAP_INV = {v: k for k, v in MESES_MAP.items()}

def es_ultimo_dia_febrero(fecha):
    """Detecta si es 28 o 29 de febrero"""
    return fecha.month == 2 and fecha.day == calendar.monthrange(fecha.year, 2)[1]


def normalizar_dia(d):
    """
    Retorna el día normalizado (no modifica la fecha)
    """
    if d.day == 31 or es_ultimo_dia_febrero(d):
        return 30
    return d.day


def dias_360(inicio, fin):
    """
    Cálculo 30/360 SIN modificar fechas reales
    """
    d1 = normalizar_dia(inicio)
    d2 = normalizar_dia(fin)

    return (
        (fin.year - inicio.year) * 360 +
        (fin.month - inicio.month) * 30 +
        (d2 - d1)
    ) + 1


def dias_por_mes_360(fecha_inicio, fecha_fin, incluir_mes_actual=True):
    """
    Retorna meses en TEXTO + días trabajados en formato 30/360
    """

    # Si viene como string
    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, "%d-%m-%Y").date()

    resultado = {}

    current = fecha_inicio.replace(day=1)

    while current <= fecha_fin:
        year = current.year
        month = current.month

        inicio_mes = date(year, month, 1)
        ultimo_dia = calendar.monthrange(year, month)[1]
        fin_mes = date(year, month, ultimo_dia)

        inicio_real = max(fecha_inicio, inicio_mes)
        fin_real = min(fecha_fin, fin_mes)

        # 🔴 lógica de inclusión del mes inicial
        if not incluir_mes_actual and month == fecha_inicio.month:
            current = date(year + (month // 12), ((month % 12) + 1), 1)
            continue

        if inicio_real <= fin_real:
            dias = dias_360(inicio_real, fin_real)

            nombre_mes = MESES_MAP_INV.get(month)
            resultado[nombre_mes] = dias

        # avanzar mes
        if month == 12:
            current = date(year + 1, 1, 1)
        else:
            current = date(year, month + 1, 1)

    return resultado

def salario_base_cesantias(contrato, salario_minimo, aux_transporte_val):
    # Excluidos por ley
    if contrato.tipocontrato.idtipocontrato == 5 or contrato.tiposalario.idtiposalario == 2:
        return 0, 0

    salario_base = contrato.salario
    transporte = 0

    if contrato.salario < (2 * salario_minimo):
        salario_base += aux_transporte_val
        transporte = aux_transporte_val

    return salario_base, transporte


def cesantia_normal(contrato, dias, salario_minimo, aux_transporte_val):
    salario_base, transporte = salario_base_cesantias(
        contrato,
        salario_minimo,
        aux_transporte_val
    )

    if dias <= 0 or salario_base == 0:
        return 0, transporte

    valor = round((salario_base * dias) / 360, 2)
    return valor, transporte

def intereses_cesantias(valor_cesantias, dias):
    if valor_cesantias <= 0 or dias <= 0:
        return 0

    return round((valor_cesantias * 0.12 * dias) / 360, 2)





class SeveranceForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        self.fields['year'] = forms.ChoiceField(
            choices=[('', '----------')] + [(years.idano, f" {years.ano}" ) for years in Anos.objects.all().order_by('-idano')], 
            label='Año a calcular' ,
            widget=forms.Select(attrs={
                'data-control': 'select2',
                'class': 'form-select',
                'data-hide-search': 'true',
            }), 
            )

        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'form_bonus'
        
        self.helper.layout = Layout(
            Row(
                Column('year', css_class='form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column(
                    Div(
                        Submit('submit', 'Generar', css_class='btn btn-primary w-100'),
                        css_class='d-grid'  # para que el botón ocupe todo el ancho de la columna
                    ),
                    css_class='form-group col-md-12 mb-3'
                ),
                css_class='row'
            )
            
        )



@login_required
@role_required('accountant')
def severance_annual_calculation(request):

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


    usuario = request.session.get('usuario', {})
    idempresa = usuario.get('idempresa')
    contratos_activos = []
    contratos_empleados = []
    year = 0
    form = SeveranceForm()

    # 🔹 Traer conceptos fijos UNA SOLA VEZ
    conceptos = Conceptosfijos.objects.filter(
        conceptofijo__in=['CESANTIAS', 'Intereses de Cesantias',]
    ).values_list('conceptofijo', 'valorfijo')
    conceptos_dict = {c[0]: c[1] for c in conceptos}

    # =========================
    # PROVISIONES MENSUALES (%)
    # =========================

    # Cesantías:
    # Legalmente equivalen a 1 salario por año (100%)
    # → Provisión mensual = 100% / 12 = 8.3333%
    ccp = to_decimal(conceptos_dict.get('CESANTIAS'), '8.3333')

    # Intereses de cesantías:
    # 12% anual sobre cesantías
    # → Provisión mensual = 12% / 12 = 1%
    iccp = to_decimal(conceptos_dict.get('Intereses de Cesantias'), '12.00')

    if request.method == 'POST':
        form = SeveranceForm(request.POST)

        if form.is_valid():

            year_id = form.cleaned_data.get('year') or 0
            year_obj = Anos.objects.get(idano=year_id)

            # Asumiendo que el año está en un campo tipo: year_obj.ano
            year = year_obj.ano  
            # Primer día del año
            first_day = date(year, 1, 1)
            # Último día del año
            last_day = date(year, 12, 31)

            sal_min = Salariominimoanual.objects.get(ano=year).salariominimo
            aux_tra = Salariominimoanual.objects.get(ano=year).auxtransporte

            contratos_activos = Contratos.objects.filter(
                estadocontrato=1,
                estadoliquidacion='3',
                idcontrato__in=[7934,7938,7939],
                #idcontrato__in=[7962,7974,12071],
                #idcontrato = 7938, 
                tipocontrato__idtipocontrato__in=[1, 2, 3, 4],
                fechainiciocontrato__lte=last_day,
                id_empresa = idempresa,
            ).filter(
                Q(fechafincontrato__isnull=True) |
                Q(fechafincontrato__gte=first_day)
            )

            for c in contratos_activos:

                fecha_inicio = max(c.fechainiciocontrato,first_day)
                fecha_fin = last_day

                if fecha_inicio > fecha_fin:
                    dias = 0
                else:
                    dias = dias_360(fecha_inicio, fecha_fin)
                
                salario_basico = salario_mes(c , fecha_inicio.month, fecha_inicio.year)
                transporte_mes = transporte_auxiliar(c,sal_min, aux_tra, fecha_inicio.month, fecha_inicio.year)

                cc , intr ,ccr , extras = valor_cesantias(c,year,fecha_inicio,fecha_fin, iccp, ccp , salario_basico , transporte_mes)  
                
                contratos_empleados.append({
                        'idcontrato': c.idcontrato,
                        'idempleado__docidentidad': c.idempleado.docidentidad,
                        'idempleado__papellido': c.idempleado.papellido,
                        'idempleado__pnombre': c.idempleado.pnombre,
                        'fechainiciocontrato': c.fechainiciocontrato,
                        'salario': salario_basico , 
                        'extras': extras,
                        'dias_cesantias': dias,
                        'dias_suspension': dias_suspension(c,year, fecha_inicio, fecha_fin),
                        'trans': transporte_mes ,
                        'valor_cesantias':ccr,
                        'valor_cesantias_r':cc,
                        'intereses_cesantias': intr,
                        
                        # Para fondo 
                        'fondo_cesantias': c.fondocesantias.entidad if c.fondocesantias else '' ,
                    })

    context = {
        'contratos_empleados': contratos_empleados,
        'form': form,
        'year': year,
    }

    return render(request,'payroll/severance_annual_calculation.html',context)



@login_required
@role_required('accountant')
def severance_monthly_detail(request, idc, year):

    def to_decimal(value, default):
        try:
            if value is None:
                return Decimal(default)
            return Decimal(str(value).replace(',', '.'))
        except:
            return Decimal(default)

    # 🔹 Conceptos
    conceptos = Conceptosfijos.objects.filter(
        conceptofijo__in=['CESANTIAS', 'Intereses de Cesantias']
    ).values_list('conceptofijo', 'valorfijo')

    conceptos_dict = {c[0]: c[1] for c in conceptos}

    icc = to_decimal(conceptos_dict.get('Intereses de Cesantias'), '12')  # 12% anual

    contrato = Contratos.objects.get(idcontrato=idc)
    year_obj = Anos.objects.get(ano=year)

    year = year_obj.ano
    first_day = date(year, 1, 1)
    last_day = date(year, 12, 31)

    sal_min = Salariominimoanual.objects.get(ano=year).salariominimo
    aux_tra = Salariominimoanual.objects.get(ano=year).auxtransporte

    fecha_inicio = max(contrato.fechainiciocontrato, first_day)
    fecha_fin = last_day

    dias_por_mes = dias_por_mes_360(fecha_inicio, fecha_fin)

    nomina_list = []

    total_cesantias_acumuladas = Decimal('0.0')

    for mes_nombre, dias in dias_por_mes.items():

        dias = Decimal(dias)

        base_mes = (
            Nomina.objects.filter(
                idcontrato=contrato,
                estadonomina=2,
                idnomina__anoacumular__ano=year,
                idnomina__mesacumular=mes_nombre,
                idconcepto__indicador__nombre='baseprima'
            ).aggregate(total=Sum('valor'))['total'] or 0
        )


        transporte_mes = (
            Nomina.objects.filter(
                idcontrato=contrato,
                estadonomina=2,
                idnomina__anoacumular__ano=year,
                idnomina__mesacumular=mes_nombre,
                idconcepto__codigo= 2 # Transporte
                #idconcepto__codigo__in=[1,4,42]
            )
            .aggregate(total=Sum('valor'))['total']
            or 0
        )
        
    

        #for base_mes_aux in base_mes_aux:

            #print(f"Concepto: {base_mes_aux.idconcepto.nombreconcepto} | Valor: {base_mes_aux.valor} | cantidad: {base_mes_aux.cantidad} - mes: {base_mes_aux.idnomina.mesacumular} ")
        
        salarios_mes = (
            Nomina.objects.filter(
                idcontrato=contrato,
                estadonomina=2,
                idnomina__anoacumular__ano=year,
                idnomina__mesacumular=mes_nombre,
                idconcepto__indicador__nombre='extras'
                #idconcepto__codigo__in=[1,4,42]
            )
            .aggregate(total=Sum('valor'))['total']
            or 0
        )

        if salarios_mes != 0:
            extras = salarios_mes 
        else:
            extras = 0

        

        sueldo_basico = Decimal(salario_mes(contrato, fecha_inicio.month, fecha_inicio.year))

        transporte = Decimal(transporte_auxiliar(contrato, sal_min, aux_tra, fecha_inicio.month, fecha_inicio.year)) or 0

        #base_mes = Decimal(base_mes) + Decimal(transporte_mes)
        # 
        cesantias_mes = (base_mes) * (Decimal(30) / Decimal(360))

        # 🔹 Acumular cesantías
        total_cesantias_acumuladas += cesantias_mes

        # ✅ INTERESES CORRECTOS (sobre cesantías acumuladas)
        intereses_mes = (
            total_cesantias_acumuladas * (icc / Decimal('100')) * (dias / Decimal(360))
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        suspensiones = Decimal('0')
        vacaciones = Decimal('0')

        total = cesantias_mes + intereses_mes

        nomina_list.append({
            "mes": mes_nombre,
            "ano": year,
            "sueldo_basico": float(sueldo_basico),
            "base_mes": float(base_mes),
            "extras":extras,
            "transporte": float(transporte),
            "cesantias": float(cesantias_mes),
            "intereses": float(intereses_mes),
            "suspensiones": float(suspensiones),
            "vacaciones": float(vacaciones),
            "dias": int(dias),
            "total": float(total),
        })

    context = {
        "data": {
            "id": contrato.idcontrato,
            "nomina": nomina_list
        }
    }

    return render(request, 'payroll/severance_monthly_detail.html', context)


def extras(contrato,year, fecha_inicio, fecha_fin):
    dias_por_mes = dias_por_mes_360(fecha_inicio, fecha_fin)


    dias_por_mes = dias_por_mes_360(fecha_inicio, fecha_fin)

    resultado = {}
    total_cesantias = Decimal('0.0')
    dias_cesantias = 0

    for mes_nombre, dias in dias_por_mes.items():

        base_mes = (
            Nomina.objects.filter(
                idcontrato=contrato,
                estadonomina=2,
                idnomina__anoacumular__ano=year,
                idnomina__mesacumular=mes_nombre,
                idconcepto__indicador__nombre='baseprima'
            )
            .aggregate(total=Sum('valor'))['total']
            or 0
        )


        salarios_mes = (
            Nomina.objects.filter(
                idcontrato=contrato,
                estadonomina=2,
                idnomina__anoacumular__ano=year,
                idnomina__mesacumular=mes_nombre,
                idconcepto_codigo__in=[1,2,4,42]
            )
            .aggregate(total=Sum('valor'))['total']
            or 0
        )

        extras = salarios_mes - base_mes

        resultado[mes_nombre] = {
            'dias': dias,
            'base': float(base_mes),
            'extras': float(extras)
        }

        total_cesantias += extras
        dias_cesantias += dias

    return 0


def dias_suspension(contrato,year, fecha_inicio, fecha_fin):

    dias_por_mes = dias_por_mes_360(fecha_inicio, fecha_fin)

    resultado = {}
    total_dias_suspension = 0

    for mes_nombre, dias in dias_por_mes.items():
        
        base_mes = (
            Nomina.objects.filter(
                idcontrato=contrato,
                estadonomina=2,
                idnomina__anoacumular__ano=year,
                idnomina__mesacumular=mes_nombre,
                idconcepto__indicador__nombre='suspcontrato'
            )
            .aggregate(total=Sum('cantidad'))['total']
            or 0
        )

        total_dias_suspension += base_mes

    dias = total_dias_suspension or 0
    return dias



def transporte_auxiliar(contrato,sal_min, aux_tra , mes , ano ):
    salario = salario_mes(contrato, mes, ano)
    if contrato.tipocontrato_id in (5, 6):
        return 0
    if contrato.auxiliotransporte:
        return 0
    if salario >= (sal_min * 2):
        return 0

    return aux_tra



def valor_cesantias(contrato, year, fecha_inicio, fecha_fin , cons_int , cons_ces , salario_mes ,transporte_mes):

    dias_por_mes = dias_por_mes_360(fecha_inicio, fecha_fin)

    resultado = {}


    total_cesantias = Decimal('0.0')
    total_intereses_base = Decimal('0.0')
    dias_cesantias = 0
    base_mes = Decimal('0.0')
    extras_mes = Decimal('0.0')
    total_extras = Decimal('0.0')

    D360 = Decimal(360)
    TASA = Decimal('0.12')
    TASA2 = Decimal(cons_int) * Decimal(12) / Decimal(100)

    # helper para redondear hacia arriba a entero
    def ceil_int(valor):
        return int(valor.to_integral_value(rounding=ROUND_CEILING))

    for mes_nombre, dias in dias_por_mes.items():

        base_mes = (
            Nomina.objects.filter(
                idcontrato=contrato,
                estadonomina=2,
                idnomina__anoacumular__ano=year,
                idnomina__mesacumular=mes_nombre,
                idconcepto__indicador__nombre='basecesantias'
            ).aggregate(total=Sum('valor'))['total'] or 0
        )

        extras_mes = (
            Nomina.objects.filter(
                idcontrato=contrato,
                estadonomina=2,
                idnomina__anoacumular__ano=year,
                idnomina__mesacumular=mes_nombre,
                idconcepto__indicador__nombre='extras'
            ).aggregate(total=Sum('valor'))['total'] or 0
        )

        base_mes = Decimal(base_mes) 
        dias = Decimal(dias)

        cesantia_mes = base_mes * Decimal(cons_ces) / Decimal(100)
        cesantia_mes_r = (base_mes * dias) / D360

        interes_base_mes = cesantia_mes

        total_cesantias += cesantia_mes
        total_intereses_base += interes_base_mes
        total_extras += extras_mes

        resultado[mes_nombre] = {
            'dias': int(dias),
            'base': ceil_int(base_mes),
            'cesantia': ceil_int(cesantia_mes),
            'cesantia_r': ceil_int(cesantia_mes_r),
            'interes': ceil_int(interes_base_mes * TASA)
        }

        dias_cesantias += int(dias)

    total_intereses = total_intereses_base * TASA

    #print(f'----------------{contrato.idcontrato}---------------')
    #print('Cesantías:', total_cesantias)
    #print('Intereses:', total_intereses)
    #print('Extras:', total_extras)
    #print(resultado)
    #print('----------------')

    total_cesantias_acumuladas = (salario_mes * 12) + (transporte_mes * 12 )+ total_extras

    total_cesantias_acumuladas = total_cesantias_acumuladas * Decimal(cons_ces) / Decimal(100)
    factor_dias = Decimal(dias_cesantias) / D360
    intereses_final = total_cesantias_acumuladas * TASA2 * factor_dias

    # retorno en enteros redondeados hacia arriba
    return ceil_int(total_cesantias), ceil_int(intereses_final) , ceil_int(total_cesantias_acumuladas) , ceil_int(total_extras/12)


