
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Tipodenomina , Conceptosdenomina ,Nomina, Crearnomina , Contratos , Anos, Liquidacion , Salariominimoanual , Nomina,Vacaciones
from apps.payroll.forms.BonusForm import BonusForm , BonusAddForm
from datetime import datetime, timedelta ,date
from dateutil.relativedelta import relativedelta



def calcular_dias_cesantias(fecha_inicio, fecha_fin):
    """
    Cálculo legal colombiano:
    Días calendario reales, incluyendo el último día.
    """
    if fecha_inicio > fecha_fin:
        return 0
    return (fecha_fin - fecha_inicio).days + 1



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


@login_required
@role_required('accountant')
def severance_annual_calculation(request):

    usuario = request.session.get('usuario', {})
    idempresa = usuario.get('idempresa')
    contratos_empleados = []

    form = BonusForm()
    date_init_str = date_end_str = ''
    proy = 0

    if request.method == 'POST':
        form = BonusForm(request.POST)

        if form.is_valid():
            date_init_str = form.cleaned_data['init_Date']
            date_end_str = form.cleaned_data['end_date']
            proy = form.cleaned_data.get('estimated_bonus') or 0

            date_init = datetime.strptime(date_init_str, '%d-%m-%Y').date()
            date_end = datetime.strptime(date_end_str, '%d-%m-%Y').date()
            año_actual = date_end.year

            try:
                sm = Salariominimoanual.objects.get(ano=año_actual)
                salario_minimo = sm.salariominimo
                aux_transporte_val = sm.auxtransporte
            except Salariominimoanual.DoesNotExist:
                salario_minimo = 0
                aux_transporte_val = 0

            contratos = Contratos.objects.select_related(
                'idempleado', 'tipocontrato', 'tiposalario','fondocesantias',
            ).filter(
                estadocontrato=1,
                tipocontrato__idtipocontrato__in=[1, 2, 3, 4],
                id_empresa_id=idempresa
            )

            for c in contratos:

                # 🔹 Determinar rango legal
                fecha_inicio = max(c.fechainiciocontrato, date(año_actual, 1, 1))
                fecha_fin = min(date_end, date(año_actual, 12, 31))

                if fecha_inicio > fecha_fin:
                    dias = 0
                else:
                    dias = calcular_dias_cesantias(fecha_inicio, fecha_fin)

                    if proy > 0 and fecha_fin < date(año_actual, 12, 31):
                        dias += proy

                # 🔹 Cesantías + auxilio
                valor_cesantias, transporte = cesantia_normal(
                    c,
                    dias,
                    salario_minimo,
                    aux_transporte_val
                )

                # 🔹 Intereses
                intereses = intereses_cesantias(valor_cesantias, dias)

                contratos_empleados.append({
                    'idcontrato': c.idcontrato,
                    'idempleado__docidentidad': c.idempleado.docidentidad,
                    'idempleado__papellido': c.idempleado.papellido,
                    'idempleado__pnombre': c.idempleado.pnombre,
                    'fechainiciocontrato': c.fechainiciocontrato,
                    'salario': c.salario,

                    # Campos legales
                    'trans': transporte,
                    'extra': 0,
                    'dias_cesantias': dias,
                    'valor_cesantias': valor_cesantias,
                    'intereses_cesantias': intereses,

                    # Para fondo 
                    'fondo_cesantias': c.fondocesantias ,
                })

    context = {
        'contratos_empleados': contratos_empleados,
        'form': form,
        'date_init_str': date_init_str,
        'date_end_str': date_end_str,
        'proy': proy,
    }

    return render(
        request,
        'payroll/severance_annual_calculation.html',
        context
    )



