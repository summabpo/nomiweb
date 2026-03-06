from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Tipodenomina , Conceptosdenomina ,Nomina, Crearnomina , Contratos , Anos, Liquidacion , Salariominimoanual , Nomina,Vacaciones
from django.http import HttpResponse
from django.urls import reverse
from apps.payroll.forms.SettlementForm import SettlementForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime , date
from .liquidacion_utils import *
from django.db.models import Q
from django.utils import timezone
from datetime import date
from decimal import Decimal



MES_CHOICES = [
    ('', '--------------'),
    ('ENERO', 'Enero'),
    ('FEBRERO', 'Febrero'),
    ('MARZO', 'Marzo'),
    ('ABRIL', 'Abril'),
    ('MAYO', 'Mayo'),
    ('JUNIO', 'Junio'),
    ('JULIO', 'Julio'),
    ('AGOSTO', 'Agosto'),
    ('SEPTIEMBRE', 'Septiembre'),
    ('OCTUBRE', 'Octubre'),
    ('NOVIEMBRE', 'Noviembre'),
    ('DICIEMBRE', 'Diciembre')
]


@login_required
@role_required('accountant')
def settlement_list(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    settlements = Liquidacion.objects.filter(idcontrato__id_empresa = idempresa 
            ).order_by('-idliquidacion'
            ).values(   
                'idcontrato__idcontrato',
                'idcontrato__idempleado__docidentidad',
                'idcontrato__idempleado__papellido',
                'idcontrato__idempleado__pnombre',
                'idcontrato__idempleado__sapellido',
                'idcontrato__idempleado__snombre',
                'diastrabajados',
                'idcontrato__fechainiciocontrato',
                'idliquidacion',
                'fechafincontrato',
                'cesantias',
                'intereses',
                'prima',
                'vacaciones',
                'totalliq',
                'estadoliquidacion',
                
                )


    return render(request, './payroll/settlement_list.html',{'settlements': settlements})

@login_required
@role_required('accountant')
def settlement_list_payroll(request, id,url):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    nominas = Crearnomina.objects.filter(estadonomina=True, id_empresa_id=idempresa).order_by('-idnomina')

    # 🔧 Función auxiliar para convertir a número de forma segura
    def to_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0
        
    def safe_decimal(value, max_value=999.99):
        """Convierte a decimal y limita al rango permitido por el modelo"""
        try:
            val = float(value)
            if val > max_value:
                return max_value
            if val < 0:
                return 0
            return val
        except (TypeError, ValueError):
            return 0

    if request.method == 'POST':
        ahora = timezone.localtime(timezone.now())
        hoy = date.today()
        
        id_nomina = request.POST.get('nomina')
        nueva_nomina_flag = request.POST.get('nueva_nomina') == 'on'
        
        nomina_final = None
        
        # 🔹 Caso 1: crear nueva nómina automática
        if nueva_nomina_flag:
            nomina_final = Crearnomina.objects.create(
                nombrenomina=f"Nomina Aut. Liqui - {ahora.strftime('%Y-%m-%d %H:%M:%S')}",
                fechainicial=hoy,
                fechafinal=hoy,
                fechapago=ahora.date(),
                tiponomina=Tipodenomina.objects.get(tipodenomina='Liquidación'),
                mesacumular= MES_CHOICES[ahora.month][0] if ahora.month else '',
                anoacumular=Anos.objects.get(ano=ahora.year),
                estadonomina=True,
                diasnomina=1,
                id_empresa_id=idempresa,
            )
        
        else:
            if id_nomina:
                nomina_final = Crearnomina.objects.filter(
                    idnomina=id_nomina, id_empresa_id=idempresa
                ).first()

            # Validar: si no existe la nómina seleccionada → crear una nueva automática
            if not nomina_final:
                nomina_final = Crearnomina.objects.create(
                    nombrenomina=f"Nomina Aut. Liqui - {ahora.strftime('%Y-%m-%d %H:%M:%S')}",
                    fechainicial=hoy,
                    fechafinal=hoy,
                    fechapago=ahora.date(),
                    tiponomina=Tipodenomina.objects.get(tipodenomina='Liquidación'),
                    mesacumular= MES_CHOICES[ahora.month][0] if ahora.month else '',
                    anoacumular=Anos.objects.get(ano=ahora.year),
                    estadonomina=True,
                    diasnomina=1,
                    id_empresa_id=idempresa,
                )

        #nomina_creada = get_object_or_404(Crearnomina, idnomina=id_nomina)
        liquidacion = get_object_or_404(Liquidacion, idliquidacion=id)

        conceptos = {
            'prima': 23,
            'vacaciones': 32,
            'cesantias': 20,
            'intereses': 21,
            'indemnizacion': 35,
        }

        # 🔹 Cargamos todos los conceptos de una sola vez (menos queries)
        conceptos_qs = Conceptosdenomina.objects.filter(
            codigo__in=conceptos.values(),
            id_empresa_id=idempresa
        )
        conceptos_dict = {c.codigo: c for c in conceptos_qs}

        # 🔹 Mapeo automático de campos a crear en nómina
        campos = [
            ('prima', 'diasprimas', 23),
            ('vacaciones', 'diasvacaciones', 32),
            ('cesantias', 'diascesantias', 20),
            ('intereses', 'diascesantias', 21),
            ('indemnizacion', None, 35),
        ]

        # 🔹 Generación de registros dinámica
        for attr_valor, attr_cantidad, codigo in campos:
            valor = to_float(getattr(liquidacion, attr_valor, 0))
            
            if valor <= 0:
                continue

            cantidad = safe_decimal(getattr(liquidacion, attr_cantidad, 0)) if attr_cantidad else Decimal('0')
            
            Nomina.objects.create(
                valor=valor,
                cantidad=cantidad,
                idconcepto=conceptos_dict.get(codigo),
                idnomina=nomina_final,
                estadonomina=1,
                idcontrato=liquidacion.idcontrato,
            )

        # 🔹 Actualiza el estado de la liquidación
        liquidacion.estadoliquidacion = 3
        liquidacion.save(update_fields=['estadoliquidacion'])

        # 🔹 Respuesta Unpoly
        response = HttpResponse()
        response['X-Up-Accept-Layer'] = 'true'
        response['X-Up-icon'] = 'success'
        response['X-Up-Message'] = 'La liquidación se envió correctamente a la nómina correspondiente'
        
        
        if url == 0:
            response['X-Up-Location'] = reverse('payroll:settlement_list')
        else:
            response['X-Up-Location'] = reverse('companies:settlementlist')
            
        return response

    return render(request, './payroll/partials/settlement_payroll.html', {
        'nominas': nominas,
        'id': id,
        'url':url,
    })



@login_required
@role_required('accountant')
def settlement_create(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    form = SettlementForm(idempresa = idempresa)
    if request.method == 'POST':
        form = SettlementForm(request.POST , idempresa=idempresa )
        if form.is_valid():
            contract_id = request.POST.get('contract')
            end_date_str = request.POST.get('end_date')
            reason = request.POST.get('reason_for_termination')
            if not (contract_id and end_date_str and reason):
                return JsonResponse({'error': 'Datos incompletos'}, status=400)

            try:
                contrato = Contratos.objects.get(idcontrato=contract_id)
                fecha_inicio = contrato.fechainiciocontrato
                fecha_fin = datetime.strptime(end_date_str, '%d-%m-%Y').date()
            except Contratos.DoesNotExist:
                return JsonResponse({'error': 'Contrato no encontrado'}, status=404)
            except ValueError:
                return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)

            if fecha_fin < fecha_inicio:
                return JsonResponse({'error': 'La fecha final debe ser posterior al inicio del contrato'}, status=400)

            # Datos base
            salario = contrato.salario
            salario_min_obj = Salariominimoanual.objects.filter(ano=fecha_fin.year).first()
            if not salario_min_obj:
                return JsonResponse({'error': 'No hay salario mínimo definido para ese año'}, status=400)

            salario_minimo = salario_min_obj.salariominimo
            aux_transporte = 0 if salario > (2 * salario_minimo) else salario_min_obj.auxtransporte

            dias_trabajados = dias_360(fecha_inicio, fecha_fin)
            fecha_cesantias = obtener_fecha_cesantias(fecha_inicio, fecha_fin)
            dias_cesantias = dias_360_2(fecha_cesantias, fecha_fin)

            fecha_prima = obtener_fecha_prima(fecha_inicio, fecha_fin)
            dias_prima = dias_360_2(fecha_prima, fecha_fin)

            # Conceptos
            extras_y_comisiones_qs = Conceptosdenomina.objects.filter(Q(indicador__nombre='extras') | Q(indicador__nombre='comisiones') ,id_empresa = idempresa)
            suspensiones_qs = Conceptosdenomina.objects.filter( indicador__nombre = 'suspcontrato',id_empresa = idempresa)
            recargos_qs = Conceptosdenomina.objects.filter(codigo=3 ,id_empresa = idempresa )

            # Acumulados
            acum_cesantias = acumular_por_mes(Nomina, extras_y_comisiones_qs, contrato.idcontrato, fecha_fin.year, fecha_cesantias.month, fecha_fin.month)
            acum_prima = acumular_por_mes(Nomina, extras_y_comisiones_qs, contrato.idcontrato, fecha_fin.year, fecha_prima.month, fecha_fin.month)
            acum_susp = acumular_por_mes(Nomina, suspensiones_qs, contrato.idcontrato, fecha_fin.year, fecha_cesantias.month, fecha_fin.month, campo='cantidad')
            acum_recargos = acumular_por_mes(Nomina, recargos_qs, contrato.idcontrato, fecha_fin.year, fecha_cesantias.month, fecha_fin.month)

            # Días efectivos
            dias_efectivos_cesantias = dias_cesantias - acum_susp
            dias_efectivos_prima = dias_prima - acum_susp

            # Bases
            base_cesantias = calcular_base_promedio(acum_cesantias, dias_efectivos_cesantias, salario, aux_transporte)
            base_prima = calcular_base_promedio(acum_prima, dias_efectivos_prima, salario, aux_transporte)
            base_vacaciones = calcular_base_vacaciones(acum_recargos, dias_cesantias, salario)

            # Vacaciones
            dias_susp_vac = Nomina.objects.filter(
                idcontrato=contrato.idcontrato,
                estadonomina=2,
                idconcepto__id_empresa = idempresa,
                idconcepto__indicador__nombre='suspcontrato'
            ).aggregate(total=Sum('cantidad'))['total'] or 0

            dias_vac_generados = (dias_trabajados - dias_susp_vac) * 15 / 360
            
            dias_vac_tomados = Vacaciones.objects.filter(idcontrato=contrato.idcontrato).aggregate(total=Sum('diasvac'))['total'] or 0
            dias_vacaciones = round(dias_vac_generados - (dias_vac_tomados or 0), 2)

            
            
            # Componentes de liquidación
            prima = calcular_prima(dias_prima, base_prima)
            cesantias = calcular_cesantias(dias_efectivos_cesantias, base_cesantias)
            vacaciones = calcular_vacaciones(dias_vacaciones, base_vacaciones)
            intereses = calcular_intereses_cesantias(dias_cesantias, cesantias)
            indemnizacion = calcular_indemnizacion(salario, dias_trabajados, reason)

            total_liquidacion = prima + cesantias + vacaciones + intereses + indemnizacion
            
            liquidacion = Liquidacion.objects.create(
                diastrabajados = dias_trabajados ,
                cesantias = cesantias,
                prima = prima,
                vacaciones = vacaciones,
                intereses = intereses,
                totalliq = total_liquidacion,
                diascesantias = dias_cesantias,
                diasprimas = dias_prima,
                diasvacaciones = dias_vacaciones,
                baseprima = base_prima,
                basecesantias = base_cesantias,
                basevacaciones = base_vacaciones,
                idcontrato = contrato ,  #fk principal 
                fechainiciocontrato = fecha_inicio,
                fechafincontrato = fecha_fin,
                salario = salario,
                motivoretiro = reason,
                estadoliquidacion = '1',
                diassusp = dias_susp_vac,
                indemnizacion = indemnizacion,
                diassuspv = dias_susp_vac,
            )

            contrato = Contratos.objects.get(idcontrato=contract_id)
            contrato.fechafincontrato = datetime.strptime(end_date_str, '%d-%m-%Y').date()
            contrato.save()
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Liquidacion guardada exitosamente'    
            response['X-Up-Location'] = reverse('payroll:settlement_list')           
            return response
    
    return render(request, './payroll/partials/settlement_create.html',{'form': form})



@require_POST
def settlement_calculate(request):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    
    contract_id = request.POST.get('contract')
    end_date_str = request.POST.get('end_date')
    reason = request.POST.get('reason_for_termination')

    if not (contract_id and end_date_str and reason):
        return JsonResponse({'error': 'Datos incompletos'}, status=400)

    try:
        contrato = Contratos.objects.get(idcontrato=contract_id)
        fecha_inicio = contrato.fechainiciocontrato
        fecha_fin = datetime.strptime(end_date_str, '%d-%m-%Y').date()
    except Contratos.DoesNotExist:
        return JsonResponse({'error': 'Contrato no encontrado'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)

    if fecha_fin < fecha_inicio:
        return JsonResponse({'error': 'La fecha final debe ser posterior al inicio del contrato'}, status=400)

    # Datos base
    salario = contrato.salario
    salario_min_obj = Salariominimoanual.objects.filter(ano=fecha_fin.year).first()
    if not salario_min_obj:
        return JsonResponse({'error': 'No hay salario mínimo definido para ese año'}, status=400)
        
    dias_susp_vac = Nomina.objects.filter(
        idcontrato=contrato.idcontrato,
        estadonomina=2,
        idconcepto__id_empresa = idempresa,
        idconcepto__indicador__nombre='suspcontrato'
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    
    
    salario_minimo = salario_min_obj.salariominimo
    aux_transporte = 0 if salario > (2 * salario_minimo) else salario_min_obj.auxtransporte

    dias_trabajados = dias_360(fecha_inicio, fecha_fin)
    fecha_cesantias = obtener_fecha_cesantias(fecha_inicio, fecha_fin)
    dias_cesantias = dias_360_2(fecha_cesantias, fecha_fin) + 1

    fecha_prima = obtener_fecha_prima(fecha_inicio, fecha_fin)
    dias_prima = dias_360_2(fecha_prima, fecha_fin) + 1 

    # Conceptos
    extras_y_comisiones_qs = Conceptosdenomina.objects.filter(Q(indicador__nombre='extras') | Q(indicador__nombre='comisiones') ,id_empresa = idempresa)
    suspensiones_qs = Conceptosdenomina.objects.filter( indicador__nombre = 'suspcontrato',id_empresa = idempresa)
    recargos_qs = Conceptosdenomina.objects.filter(codigo=3 ,id_empresa = idempresa )

    # Acumulados
    acum_cesantias = acumular_por_mes(Nomina, extras_y_comisiones_qs, contrato.idcontrato, fecha_fin.year, fecha_cesantias.month, fecha_fin.month)
    acum_prima = acumular_por_mes(Nomina, extras_y_comisiones_qs, contrato.idcontrato, fecha_fin.year, fecha_prima.month, fecha_fin.month)
    acum_susp = acumular_por_mes(Nomina, suspensiones_qs, contrato.idcontrato, fecha_fin.year, fecha_cesantias.month, fecha_fin.month, campo='cantidad')
    acum_recargos = acumular_por_mes(Nomina, recargos_qs, contrato.idcontrato, fecha_fin.year, fecha_cesantias.month, fecha_fin.month)

    # Días efectivos
    dias_efectivos_cesantias = dias_cesantias - dias_susp_vac
    
    
    dias_efectivos_prima = dias_prima - dias_susp_vac + 1 

    # Bases
    base_cesantias = calcular_base_promedio(acum_cesantias, dias_efectivos_cesantias, salario, aux_transporte)
    base_prima = calcular_base_promedio(acum_prima, dias_efectivos_prima, salario, aux_transporte)
    base_vacaciones = calcular_base_vacaciones(acum_recargos, dias_cesantias, salario)

    # Vacaciones
    

    dias_vac_generados = (dias_trabajados - dias_susp_vac) * 15 / 360
    dias_vac_tomados = Vacaciones.objects.filter(idcontrato=contrato.idcontrato).aggregate(total=Sum('diasvac'))['total'] or 0
    dias_vacaciones = round(dias_vac_generados - (dias_vac_tomados or 0), 2)

    # Componentes de liquidación
    prima = calcular_prima(dias_prima, base_prima)
    cesantias = calcular_cesantias(dias_efectivos_cesantias, base_cesantias)
    vacaciones = calcular_vacaciones(dias_vacaciones, base_vacaciones)
    intereses = calcular_intereses_cesantias(dias_cesantias + acum_susp, cesantias)
    indemnizacion = calcular_indemnizacion(salario, dias_trabajados, reason)

    total_liquidacion = prima + cesantias + vacaciones + intereses + indemnizacion
    
    return JsonResponse({
        'dias_trabajados': safe_value(dias_trabajados),
        'dias_prima': safe_value(dias_prima),
        'dias_cesantias': safe_value(dias_cesantias),
        'dias_vacaciones': safe_value(dias_vacaciones),
        'salario': safe_value(salario),
        'aux_transporte': safe_value(aux_transporte),
        'base_prima': safe_value(base_prima),
        'base_cesantias': safe_value(base_cesantias),
        'base_vacaciones': safe_value(base_vacaciones),
        'prima': safe_value(prima),
        'cesantias': safe_value(cesantias),
        'vacaciones': safe_value(vacaciones),
        'intereses': safe_value(intereses),
        'indemnizacion': safe_value(indemnizacion),
        'total_liquidacion': safe_value(total_liquidacion),
        'inicio_contrato': fecha_inicio or "",  # Aquí podrías usar "" si prefieres string vacío para fechas
        'fin_contrato': fecha_fin or "",
        'dias_susp_vac':dias_susp_vac,
    })


