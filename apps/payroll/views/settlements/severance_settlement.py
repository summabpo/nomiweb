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
from decimal import Decimal
from apps.components.settlement_calculate import settlement_calculate_data

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


# @login_required
# @role_required('accountant')
def settlement_list(request):

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    settlements = Liquidacion.objects.filter(idcontrato__id_empresa = idempresa 
            ).order_by('-idliquidacion'
            ).values(   
                'idliquidacion',
                'idcontrato__idcontrato',
                'idcontrato__idempleado__docidentidad',
                'idcontrato__idempleado__papellido',
                'idcontrato__idempleado__pnombre',
                'idcontrato__idempleado__sapellido',
                'idcontrato__idempleado__snombre',
                'diastrabajados',
                'idcontrato__fechainiciocontrato',
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
            contrato = Contratos.objects.get(idcontrato=contract_id)
            data = settlement_calculate_data(contract_id,end_date_str,reason)

            liquidacion, created = Liquidacion.objects.get_or_create(
                idcontrato=contrato,
                defaults={
                    'diastrabajados': data['dias_trabajados'],
                    'cesantias': data['cesantias'],
                    'prima': data['prima'],
                    'vacaciones': data['vacaciones'],
                    'intereses': data['intereses'],
                    'totalliq': data['total_liquidacion'],
                    'diascesantias': data['dias_cesantias'],
                    'diasprimas': data['dias_prima'],
                    'diasvacaciones': data['dias_vacaciones'],
                    'baseprima': data['base_prima'],
                    'basecesantias': data['base_cesantias'],
                    'basevacaciones': data['base_vacaciones'],
                    'fechainiciocontrato': data['inicio_contrato'],
                    'fechafincontrato': data['fin_contrato'],
                    'salario': data['salario'],
                    'motivoretiro': reason,
                    'estadoliquidacion': '1',
                    'diassusp': data['dias_susp_vac'],
                    'indemnizacion': data['indemnizacion'],
                    'diassuspv': data['dias_susp_vac'],
                }
            )

            if not created:
                response = HttpResponse()
                response['X-Up-Accept-Layer'] = 'true'  
                response['X-Up-icon'] = 'info'   
                response['X-Up-message'] = 'La liquidación ya existía y fue actualizada con la información reciente.'    
                response['X-Up-Location'] = reverse('payroll:settlement_list')           
                return response
            

            contrato.fechafincontrato = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            contrato.save()
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  
            response['X-Up-icon'] = 'success' 
            response['X-Up-message'] = 'Liquidacion guardada exitosamente'    
            response['X-Up-Location'] = reverse('payroll:settlement_list')           
            return response
    
    return render(request, './payroll/partials/settlement_create.html',{'form': form})



@require_POST
def settlement_calculate(request):
    
    contract_id = request.POST.get('contract')
    end_date_str = request.POST.get('end_date')
    reason = request.POST.get('reason_for_termination')

    data = settlement_calculate_data(contract_id,end_date_str,reason)

    return JsonResponse(data)


