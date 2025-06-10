from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models  import Contratosemp , Vacaciones ,Contratos , Tipoavacaus , Salariominimoanual
from apps.payroll.forms.VacationSettlementForm import VacationSettlementForm , BenefitFormSet
from datetime import datetime, timedelta ,date
from django.http import JsonResponse
from apps.components.humani import format_value_float


@login_required
@role_required('accountant')
def bonus_p_settlement(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    contratos_empleados = Contratos.objects\
        .select_related('idempleado') \
        .filter(estadocontrato=1, tipocontrato__idtipocontrato__in=[1,2,3,4], id_empresa_id=idempresa) \
        .values('idempleado__docidentidad', 'idempleado__sapellido', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre', 'idempleado__idempleado', 'idcontrato', 'fechainiciocontrato', 'salario', 'auxiliotransporte') 
    
    año_actual = datetime.now().year
    
    try:
        salario_minimo_actual = Salariominimoanual.objects.get(ano=año_actual).auxtransporte
    except Salariominimoanual.DoesNotExist:
        salario_minimo_actual = 0
    
    # Definimos los semestres con sus días máximos
    semestres = [
        {'inicio': date(año_actual, 1, 1), 'fin': date(año_actual, 6, 30), 'dias_max': 180},  # 1er semestre
        {'inicio': date(año_actual, 7, 1), 'fin': date(año_actual, 12, 31), 'dias_max': 180}   # 2do semestre
    ]
    
    for contrato in contratos_empleados:
        # Auxilio de transporte
        contrato['trans'] = salario_minimo_actual if contrato['auxiliotransporte'] else 0
        contrato['valor'] = 1000
        
        fecha_inicio_contrato = contrato['fechainiciocontrato']
        dias_prima = 0
        
        # Determinamos el semestre actual (1er o 2do)
        hoy = date.today()
        semestre_actual = None
        
        for semestre in semestres:
            if hoy >= semestre['inicio'] and hoy <= semestre['fin']:
                semestre_actual = semestre
                break
        
        if semestre_actual:
            # Calculamos días trabajados en el semestre ACTUAL (no ambos)
            inicio_calculo = max(fecha_inicio_contrato, semestre_actual['inicio'])
            fin_calculo = semestre_actual['fin']
            
            if inicio_calculo <= fin_calculo:
                dias = (fin_calculo - inicio_calculo).days + 1
                dias_prima = min(dias, semestre_actual['dias_max'])  # Máximo 180 días
        
        contrato['dias_prima'] = dias_prima
        contrato['periodo_calculado'] = semestre_actual['inicio'].strftime('%d/%m/%Y') + " - " + semestre_actual['fin'].strftime('%d/%m/%Y') if semestre_actual else "N/A"
    
    context = {
        'contratos_empleados': contratos_empleados,
    }
    
    return render(request, './payroll/bonus_p_settlement.html', context)