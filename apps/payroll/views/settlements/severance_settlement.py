from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Tipodenomina , Conceptosdenomina ,Nomina,NovSalarios, Crearnomina , Contratos , Anos, Liquidacion , Salariominimoanual , Nomina,Vacaciones
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
                control = id , 
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
    TIPE_CHOICES = [
        ('', '-------------'),
        ('1', 'Renuncia Voluntaria'),
        ('2', 'Despido sin justa causa'),
        ('3', 'Despido con justa causa'),
        ('4', 'Finalización del contrato'),
        ('5', 'Cambio a salario integral'),
        ('6', 'Muerte del trabajador'),
        ('7', 'Despido en periodo de prueba'),
    ]
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']


    contratos_choices = [('', '----------')] + [
            (
                idcontrato,
                f"{(pap or '').strip()} {(pnom or '').strip()} - {idcontrato} -  {cc}"
            )
            for pnom, pap, idcontrato , cc in
            Contratos.objects.filter(estadocontrato=1, id_empresa=idempresa)
            .order_by('idempleado__papellido')
            .values_list('idempleado__pnombre','idempleado__papellido', 'idcontrato' , 'idempleado__docidentidad')
        ]
    
    form = SettlementForm(idempresa = idempresa)
    if request.method == 'POST':
        form = SettlementForm(request.POST , idempresa=idempresa )
        if form.is_valid():
            data = request.POST

            contrato = Contratos.objects.get(idcontrato=data['contract'])

            reason = data['reason_for_termination']
            #data = settlement_calculate_data(contract_id,end_date_str,reason)

            

            liquidacion, created = Liquidacion.objects.get_or_create(
                idcontrato=contrato,
                fechafincontrato = data.get('end_date'),
                defaults={
                    'diastrabajados': data.get('dias_trabajados'),
                    'cesantias': data.get('valor_cesantias'),
                    'prima': data.get('valor_prima'),
                    'vacaciones': data.get('valor_vacaciones'),
                    'intereses': data.get('valor_intereses'),
                    'totalliq': data.get('total_liquidacion'),

                    'diascesantias': data.get('dias_cesantias'),
                    'diasprimas': data.get('dias_primas'),
                    'diasvacaciones': data.get('dias_vacaciones'),

                    'baseprima': data.get('base_primas'),
                    'basecesantias': data.get('base_cesantias'),
                    'basevacaciones': data.get('base_vacaciones'),

                    'fechainiciocontrato' : data.get('fecha_inicio'),
                    'fechafincontrato': data.get('end_date'),

                    'salario': data.get('salario_base'),

                    'motivoretiro': reason,
                    'estadoliquidacion': '1',

                    'diassusp': data.get('dias_susp_ces'),
                    'diassuspv': data.get('dias_susp_vac'),

                    'indemnizacion': data.get('valor_indemnizacion'),
                }
            )

            if not created:
                response = HttpResponse()
                response['X-Up-Accept-Layer'] = 'true'  
                response['X-Up-icon'] = 'info'   
                response['X-Up-message'] = 'La liquidación ya existía y fue actualizada con la información reciente.'    
                response['X-Up-Location'] = reverse('payroll:settlement_list')           
                return response
            

            contrato.fechafincontrato = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
            contrato.save()
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  
            response['X-Up-icon'] = 'success' 
            response['X-Up-message'] = 'Liquidacion guardada exitosamente'    
            response['X-Up-Location'] = reverse('payroll:settlement_list')           
            return response
    
    return render(request, './payroll/partials/settlement_create.html',
                    {
                        'form': form , 
                        "type_choices": TIPE_CHOICES , 
                        "e_choices": contratos_choices, 
                        })


@login_required
@role_required('accountant')
def settlement_accrued_values(request,id,fecha):


    date_obj = datetime.strptime(fecha, "%Y-%m-%d")
    mes_num = date_obj.month
    ano = date_obj.year
    contrato = Contratos.objects.get(idcontrato = id)
    meses = [
        "ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO",
        "JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"
    ]
    nomina = []

    

    mes_actual = mes_num
    ano_actual = ano

    for i in range(0, 13):

        mes_texto = meses[mes_actual-1]

        salario = salario_mes(contrato , mes_actual , ano_actual) 
        # calcular mes anterior
        

        totales = Nomina.objects.filter(
            estadonomina=2,
            idcontrato_id=id,
            idnomina__mesacumular=mes_texto,
            idnomina__anoacumular__ano=ano_actual
        ).aggregate(total=Sum('valor'))


        total_trans = Nomina.objects.filter(
            estadonomina=2,
            idcontrato_id=id,
            idnomina__mesacumular=mes_texto,
            idnomina__anoacumular__ano=ano_actual,
            idconcepto__codigo = 2 

        ).aggregate(total=Sum('valor'))


        total_extras = Nomina.objects.filter(
            estadonomina=2,
            idcontrato_id=id,
            idnomina__mesacumular=mes_texto,
            idnomina__anoacumular__ano=ano_actual,
            idconcepto__codigo__in=[5, 6, 7, 8, 9, 18]

        ).aggregate(total=Sum('valor'))


        total_otros = Nomina.objects.filter(
            estadonomina=2,
            idcontrato_id=id,
            idnomina__mesacumular=mes_texto,
            idnomina__anoacumular__ano=ano_actual,
            idconcepto__codigo__in=[5, 18]

        ).aggregate(total=Sum('valor'))


        total_incapa = Nomina.objects.filter(
            estadonomina=2,
            idcontrato_id=id,
            idnomina__mesacumular=mes_texto,
            idnomina__anoacumular__ano=ano_actual,
            idconcepto__codigo__in= [25, 26, 27, 28, 87]

        ).aggregate(total=Sum('valor'))


        total_vacas = Nomina.objects.filter(
            estadonomina=2,
            idcontrato_id=id,
            idnomina__mesacumular=mes_texto,
            idnomina__anoacumular__ano=ano_actual,
            idconcepto__codigo__in= [24, 32]

        ).aggregate(total=Sum('valor'))

        total_recargo = Nomina.objects.filter(
            estadonomina=2,
            idcontrato_id=id,
            idnomina__mesacumular=mes_texto,
            idnomina__anoacumular__ano=ano_actual,
            idconcepto__codigo__in= [3, 16]

        ).aggregate(total=Sum('valor'))

        # # Obtiene todos los valores individuales
        # registros = Nomina.objects.filter(
        #     estadonomina=2,
        #     idcontrato_id=id,
        #     idnomina__mesacumular=mes_texto,
        #     idnomina__anoacumular__ano=ano_actual,
        #     idconcepto__codigo__in=[3, 16]
        # ).values('valor', 'idconcepto__codigo', 'idnomina__mesacumular', 'idnomina__anoacumular__ano')

        # print("Registros que se van a sumar:")
        # for r in registros:
        #     print(f"Valor: {r['valor']}, Código: {r['idconcepto__codigo']}, Mes: {r['idnomina__mesacumular']}, Año: {r['idnomina__anoacumular__ano']}")

        total_no_sal = Nomina.objects.filter(
            estadonomina=2,
            idcontrato_id=id,
            idnomina__mesacumular=mes_texto,
            idnomina__anoacumular__ano=ano_actual,
            idconcepto__codigo__in= [24, 32]

        ).aggregate(total=Sum('valor'))


        nomina.append({
            "mes": mes_texto,
            "ano": ano_actual,
            "sueldo_basico": salario, 
            "transporte":total_trans['total'] or 0 ,
            "hextras":total_extras['total'] or 0 ,
            "otros":total_otros['total'] or 0 ,
            "incapacidades":total_incapa['total'] or 0 ,
            "vacaciones":total_vacas['total'] or 0 ,
            "recargos":total_recargo['total'] or 0 ,
            "no_salario":total_no_sal['total'] or 0 ,
            "total_ingresos":totales['total'] or 0 ,
            
        })

        if mes_actual == 1:
            mes_actual = 12
            ano_actual -= 1
        else:
            mes_actual -= 1

    data = {
        "id": id,
        "nomina": nomina
    }

    return render(request, './payroll/settlement_accrued_values.html',{'data':data})


def salario_mes(contrato, mes, ano):
    """
    Devuelve el salario vigente para un contrato en un mes y año específicos,
    considerando los cambios de salario.
    """
    # Salario por defecto
    salario = contrato.salario

    # Fecha del mes que queremos consultar
    fecha_consulta = date(ano, mes, 1)

    # Último cambio de salario registrado para este contrato
    cambio = NovSalarios.objects.filter(
        idcontrato=contrato
    ).order_by('-fechanuevosalario').first()  # último cambio



    if cambio:
        # Si la fecha de consulta es **antes** del cambio → salarioactual
        if fecha_consulta < cambio.fechanuevosalario:
            if cambio.salarioactual is not None:
                salario = cambio.salarioactual
                
        else:
            # Si es igual o después → nuevosalario
            if cambio.nuevosalario is not None:
                salario = cambio.nuevosalario
    
    return salario


@require_POST
def settlement_calculate(request):
    
    contract_id = request.POST.get('contract')
    end_date_str = request.POST.get('end_date')
    reason = request.POST.get('reason_for_termination')

    data = settlement_calculate_data(contract_id,end_date_str,reason)

    return JsonResponse(data)


