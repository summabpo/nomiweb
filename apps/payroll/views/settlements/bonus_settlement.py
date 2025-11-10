from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models  import Contratosemp , Vacaciones ,Contratos , Nomina , Tipoavacaus , Salariominimoanual , Conceptosdenomina , Crearnomina
from apps.payroll.forms.VacationSettlementForm import VacationSettlementForm , BenefitFormSet
from datetime import datetime, timedelta ,date
from django.http import JsonResponse
from apps.components.humani import format_value_float
from django.db.models import Sum, Q
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from apps.payroll.forms.BonusForm import BonusForm , BonusAddForm
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import reverse

@login_required
@role_required('accountant')
def bonus_p_settlement(request):
    contratos_empleados = []
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = BonusForm()

    data = Conceptosdenomina.objects.filter(
        Q(indicador__nombre='basesegsocial'),
        id_empresa=idempresa
    )

    if request.method == 'POST':
        form = BonusForm(request.POST)
        if form.is_valid():
            date_init_str = form.cleaned_data['init_Date']
            date_end_str = form.cleaned_data['end_date']
            
            date_init = datetime.strptime(date_init_str, '%d-%m-%Y').date()
            date_end = datetime.strptime(date_end_str, '%d-%m-%Y').date()
            año_actual = date_end.year

            proy = form.cleaned_data.get('estimated_bonus') or 0
            
            semestre_inicio = date(date_end.year, 1, 1) if date_end.month <= 6 else date(date_end.year, 7, 1)
            semestre_actual = {'inicio': semestre_inicio, 'fin': date_end}

            try:
                sm = Salariominimoanual.objects.get(ano=año_actual)
                salario_minimo = sm.salariominimo
                aux_transporte_val = sm.auxtransporte
            except Salariominimoanual.DoesNotExist:
                salario_minimo = 0
                aux_transporte_val = 0
                
            contratos_empleados = Contratos.objects.select_related('idempleado') \
                .filter(
                    estadocontrato=1,
                    tipocontrato__idtipocontrato__in=[1,2,3,4],
                    id_empresa_id=idempresa
                ) \
                .values(
                    'idempleado__docidentidad', 'idempleado__sapellido', 'idempleado__papellido',
                    'idempleado__pnombre', 'idempleado__snombre', 'idempleado__idempleado',
                    'idcontrato', 'fechainiciocontrato', 'salario', 'auxiliotransporte',
                    'tipocontrato', 'tiposalario'
                ).exclude(
                    tiposalario__idtiposalario=2
                )

            # Limpiar None y "no data" en nombres
            for contrato in contratos_empleados:
                for field in ['idempleado__pnombre', 'idempleado__snombre', 'idempleado__papellido', 'idempleado__sapellido']:
                    value = contrato.get(field, '')
                    if value is None or (isinstance(value, str) and value.strip().lower() == 'no data'):
                        contrato[field] = ''
                    else:
                        contrato[field] = value

                fecha_inicio = contrato['fechainiciocontrato']
                fecha_fin = date_end
                validar = 0
                anio_actual = fecha_fin.year

                limite_prima = date(anio_actual, 7, 1)
                inicio_ano = date(anio_actual, 1, 1)

                # Determinar fp y fp_base según lógica original
                if fecha_inicio <= inicio_ano:
                    fp_base = limite_prima if fecha_fin >= limite_prima else inicio_ano
                    fp = fp_base
                else:
                    if fecha_fin >= limite_prima and fecha_inicio > limite_prima:
                        fp_base = limite_prima
                        fp = fecha_inicio
                    elif fecha_fin >= limite_prima and fecha_inicio < limite_prima:
                        fp_base = limite_prima
                        fp = fp_base
                    elif fecha_fin < limite_prima and fecha_inicio < limite_prima:
                        fp_base = inicio_ano
                        fp = fecha_inicio
                    else:
                        fp_base = inicio_ano
                        fp = fecha_inicio
                        validar = 1

                # Calcular días prima
                if validar == 0:
                    fecha_fin_mas_uno = fecha_fin + timedelta(days=1)
                    diferencia = relativedelta(fecha_fin_mas_uno, fp)
                    anios, meses, dias = diferencia.years, diferencia.months, diferencia.days
                    dias_prima = anios * 360 + meses * 30 + dias
                    contrato['dias_prima'] = dias_prima + proy if dias_prima > 0 else 0
                else:
                    contrato['dias_prima'] = 0

                # Calcular valores
                contrato['valor'], contrato['pp'] = prima(
                    contrato=contrato,
                    dias_prima=contrato['dias_prima'],
                    salario_minimo=salario_minimo,
                    aux_transporte_val=aux_transporte_val,
                    semestre_actual=semestre_actual,
                    fin_calculo=date_end,
                    id_empresa=idempresa,
                    proy=proy
                )

                contrato['trans'] = aux_transporte(contrato['idcontrato'], contrato['salario'], salario_minimo, aux_transporte_val)
                contrato['extra'] = extra_auto(contrato=contrato, semestre_actual=semestre_actual, fin_calculo=date_end, id=idempresa) / contrato['dias_prima'] * 30 if contrato['dias_prima'] else 0

    context = {
        'contratos_empleados': contratos_empleados,
        'form': form,
    }

    return render(request, './payroll/bonus_p_settlement.html', context)

@login_required
@role_required('accountant')
def bonus_p_settlement_add(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = BonusAddForm(idempresa=idempresa)

    if request.method == 'POST':
        form = BonusAddForm(request.POST,idempresa=idempresa)
        if form.is_valid():
            
            method_type = form.cleaned_data['method_type']
            payroll = form.cleaned_data['Payroll']

            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Las primas fueron asociadas correctamente a la nómina seleccionada.'    
            response['X-Up-Location'] = reverse('payroll:bonus_p_settlement')           
            return response      
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")    

    return render(request, './payroll/partials/bonus_p_settlement_add.html', {'form': form})



def months_between(start_date, end_date):
    """Devuelve número aproximado de meses entre dos fechas."""
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1

def _round(d):
    """Redondeo a 2 decimales."""
    return d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def prima(contrato, dias_prima, salario_minimo, aux_transporte_val, semestre_actual, fin_calculo, id_empresa, proy=0):
    salario = contrato.get('salario') or Decimal('0')
    tipo_contrato = contrato.get('tipocontrato')
    tipo_salario = contrato.get('tiposalario')
    idcontrato = contrato.get('idcontrato')

    # Tope máximo de días reales: 180
    dias_prima_real = min(Decimal(dias_prima), Decimal(180))

    # Sumar proy y volver a limitar total a 180
    dias_prima_total = min(dias_prima_real + Decimal(proy), Decimal(180))

    # Auxilio de transporte
    aux_trans = aux_transporte(idcontrato, salario, salario_minimo, aux_transporte_val)

    # Reglas especiales: contratos o salarios no válidos
    if tipo_contrato == 5 or tipo_salario == 2:
        salario = Decimal('0')
        aux_trans = Decimal('0')

    # --- Base para cálculos ---
    crearnomina_qs = Crearnomina.objects.filter(
        fechainicial__gte=semestre_actual['inicio'],
        fechafinal__lte=fin_calculo,
        id_empresa=id_empresa
    )

    # Estimar cuántas nóminas debería haber (suponiendo quincenal)
    meses = months_between(semestre_actual['inicio'], fin_calculo)
    expected_nominas = max(1, meses * 2)  # entero

    # ----------------- EXTRAS / COMISIONES (value) -----------------
    value_agg = Nomina.objects.filter(
        idcontrato=idcontrato,
        idnomina__in=crearnomina_qs.values_list('idnomina', flat=True),
        estadonomina=2,
        idconcepto__in=Conceptosdenomina.objects.filter(
            Q(indicador__nombre='extras') | Q(indicador__nombre='comisiones'),
            id_empresa=id_empresa
        ).values_list('idconcepto', flat=True)
    ).aggregate(total=Sum('valor'))

    value = value_agg.get('total') or Decimal('0')

    value_count = Nomina.objects.filter(
        idcontrato=idcontrato,
        idnomina__in=crearnomina_qs.values_list('idnomina', flat=True),
        estadonomina=2,
        idconcepto__in=Conceptosdenomina.objects.filter(
            Q(indicador__nombre='extras') | Q(indicador__nombre='comisiones'),
            id_empresa=id_empresa
        ).values_list('idconcepto', flat=True)
    ).values('idnomina').distinct().count()

    # Si hay datos, calculamos avg por nómina y proyectamos sobre expected_nominas.
    if value_count > 0:
        avg_value_per_nomina = (value / Decimal(value_count))
        # proyectar la suma completa del periodo como promedio_existente * expected_nominas
        value = avg_value_per_nomina * Decimal(expected_nominas)
    else:
        # si no hay datos, dejamos value = 0 (o podrías usar salario como proxy)
        value = Decimal('0')

    base_variable = (value / dias_prima_real) * Decimal(30) if dias_prima_real > 0 else Decimal('0')
    total_base = salario + base_variable + aux_trans
    valor_prima = (total_base * dias_prima_total) / Decimal(360)

    # ----------------- PRIMA PROMEDIO (PP) -----------------
    variables_agg = Nomina.objects.filter(
        idcontrato=idcontrato,
        idnomina__in=crearnomina_qs.values_list('idnomina', flat=True),
        estadonomina=2,
        idconcepto__in=Conceptosdenomina.objects.filter(
            Q(indicador__nombre='basePP'),
            id_empresa=id_empresa
        ).values_list('idconcepto', flat=True)
    ).aggregate(total=Sum('valor'))

    variables = variables_agg.get('total') or Decimal('0')

    variables_count = Nomina.objects.filter(
        idcontrato=idcontrato,
        idnomina__in=crearnomina_qs.values_list('idnomina', flat=True),
        estadonomina=2,
        idconcepto__in=Conceptosdenomina.objects.filter(
            Q(indicador__nombre='basePP'),
            id_empresa=id_empresa
        ).values_list('idconcepto', flat=True)
    ).values('idnomina').distinct().count()

    # CORRECCIÓN CLAVE: usar el promedio **de las nóminas existentes** y proyectar con expected_nominas.
    if variables_count > 0:
        avg_var_per_nomina_existente = variables / Decimal(variables_count)
        # total proyectado para el periodo:
        variables_total = avg_var_per_nomina_existente * Decimal(expected_nominas)
        # frecuencia detectada por expected_nominas (si esperas >=5-6 nóminas -> quincenal)
        is_quincenal = expected_nominas >= 5
        # primapromedio: si quincenal, mensual = avg_quincenal * 2; si no, usar avg directamente
        primapromedio = avg_var_per_nomina_existente * (Decimal(2) if is_quincenal else Decimal(1))
    else:
        # sin registros: asumimos salario mensual como primapromedio
        variables_total = Decimal('0')
        primapromedio = salario
        is_quincenal = True if expected_nominas >= 5 else False

    # Calculamos pp en proporción a los días de prima
    pp = (primapromedio / Decimal(180)) * dias_prima_total

    # --- DEPURACIÓN ---
    if idcontrato == 8113:
        variables_detalle = Nomina.objects.filter(
            idcontrato=idcontrato,
            idnomina__in=crearnomina_qs.values_list('idnomina', flat=True),
            estadonomina=2,
            idconcepto__in=Conceptosdenomina.objects.filter(
                Q(indicador__nombre='basePP'),
                id_empresa=id_empresa
            ).values_list('idconcepto', flat=True)
        ).values(
            'idnomina__idnomina',
            'idconcepto__nombreconcepto',
            'idnomina__nombrenomina',
            'valor'
        ).order_by('idnomina__idnomina')

        print("🔹 Conceptos encontrados:")
        for v in variables_detalle:
            print(f"ID Nómina: {v['idnomina__idnomina']} | Concepto: {v['idconcepto__nombreconcepto']} valor: {v['valor']} nomina : {v['idnomina__nombrenomina']}")
        print('----------')
        print("dias_prima_real:", dias_prima_real)
        print("value (extras+comisiones) proyectado:", value)
        print("value_count:", value_count, "expected_nominas:", expected_nominas)
        print("variables (basePP) sum original:", variables)
        print("variables_count:", variables_count, "expected_nominas:", expected_nominas)
        print("variables_total (proyectado):", variables_total)
        print("avg_var_per_nomina_existente (si aplica):", (variables / Decimal(variables_count)) if variables_count > 0 else None)
        print("is_quincenal:", is_quincenal)
        print("primapromedio:", primapromedio)
        print("pp:", pp/2)
        print("valor_prima:", valor_prima)
        print('----------')

    return _round(valor_prima), _round(pp/2)




def extra_auto(contrato, semestre_actual, fin_calculo, id):
    value = 0
    
    idcontrato = contrato['idcontrato']
    
    
    
    # Obtener los IDs de las nóminas válidas
    ids_nominas = Crearnomina.objects.filter(
        fechainicial__gte=semestre_actual['inicio'],
        fechafinal__lte=fin_calculo,
        id_empresa=id
    ).values_list('idnomina', flat=True)
    
    # Obtener los IDs de los conceptos válidos
    ids_conceptos = Conceptosdenomina.objects.filter(
        Q(indicador__nombre='extras') | Q(indicador__nombre='comisiones'),
        id_empresa=id
    ).values_list('idconcepto', flat=True)
    
    # Filtrar las líneas de nómina relevantes
    registros = Nomina.objects.filter(
        idcontrato=idcontrato,
        idnomina__in=ids_nominas,
        estadonomina=2,
        idconcepto__in=ids_conceptos
    )
 
    
    
    # Realizar la agregación
    value = registros.aggregate(total=Sum('valor'))['total'] or Decimal('0')

    return value
    
    

def aux_transporte(idcontrato , salario, minimo,aux):
    contrato = Contratos.objects.get(idcontrato=idcontrato)
    if contrato.tipocontrato.idtipocontrato == 5 or contrato.tiposalario.idtiposalario == 2 : 
        return 0
    return aux if salario < 2 * minimo else 0


