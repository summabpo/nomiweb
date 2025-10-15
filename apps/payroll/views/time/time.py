from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.contrib import messages
from apps.common.models import Tiempos , Crearnomina , Contratos ,Nomina,Conceptosdenomina, Empresa ,Conceptosfijos ,TiemposTotales ,Sedes, Costos, Subcostos, Empresa
from django.http import HttpResponse
from django.urls import reverse
from apps.payroll.forms.SettlementForm import SettlementForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime, date, time, timedelta
from django.db.models import Q
import pandas as pd
from django.db import transaction
from django.db.models import Sum
import holidays
from openpyxl import Workbook
from io import BytesIO
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from apps.payroll.forms.TimeForm import TimeForm
from urllib.parse import urlencode
from openpyxl.styles import PatternFill

@login_required
@role_required('accountant')
def time_list(request):
    value1 = False
    value2 = False
    value3 = False
    tiempos = []

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    nominas = Crearnomina.objects.filter(
        estadonomina=True,
        id_empresa_id=idempresa
    ).order_by('-idnomina')

    selected_nomina_id = request.GET.get('datatipo')
    accion = request.GET.get('accion')
    accion2 = request.GET.get('accion2')

    contratos_empleados = (
        Contratos.objects
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede')
        .order_by('idempleado__papellido')
        .filter(estadocontrato=1, id_empresa=idempresa)
        .values(
            'idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
            'idempleado__snombre', 'fechainiciocontrato', 'cargo__nombrecargo', 'salario',
            'idcosto__nomcosto', 'tipocontrato__tipocontrato', 'centrotrabajo__tarifaarl',
            'idempleado__idempleado', 'idempleado__sapellido',
            'idcontrato', 'idsede__nombresede'
        )
    )
    
    empleados = [
        {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': ' '.join(filter(None, [
                contrato['idempleado__papellido'] if contrato['idempleado__papellido'] != 'no data' else '',
                contrato['idempleado__sapellido'] if contrato['idempleado__sapellido'] != 'no data' else '',
                contrato['idempleado__pnombre'] if contrato['idempleado__pnombre'] != 'no data' else '',
                contrato['idempleado__snombre'] if contrato['idempleado__snombre'] != 'no data' else ''
            ])),
            'idcontrato': contrato['idcontrato'],
            'salario':contrato['salario'], 
            'sede': contrato.get('idsede__nombresede')
        }
        for contrato in contratos_empleados
    ]
    # ---------- Helpers ----------
    def parse_time_obj(t):
        if t is None:
            return None
        if isinstance(t, time):
            return t
        if isinstance(t, datetime):
            return t.time()
        if isinstance(t, str):
            for fmt in ("%H:%M:%S", "%H:%M"):
                try:
                    return datetime.strptime(t, fmt).time()
                except Exception:
                    continue
        return None

    def parse_date_obj(d):
        if d is None:
            return None
        if isinstance(d, date) and not isinstance(d, datetime):
            return d
        if isinstance(d, datetime):
            return d.date()
        if isinstance(d, str):
            try:
                return datetime.strptime(d, "%Y-%m-%d").date()
            except Exception:
                pass
        return None

    def horasdescuento_to_timedelta(hd):
        if hd is None:
            return timedelta()
        if isinstance(hd, timedelta):
            return hd
        if isinstance(hd, time):
            return timedelta(hours=hd.hour, minutes=hd.minute, seconds=hd.second)
        if isinstance(hd, datetime):
            return timedelta(hours=hd.hour, minutes=hd.minute, seconds=hd.second)
        try:
            return timedelta(hours=float(hd))
        except Exception:
            return timedelta()
        
    # ---------- Función auxiliar para calcular extras ----------
    def calcular_horas_extras(tiempos_queryset):
        CO_HOLIDAYS = holidays.CO(years=2025)
        horas_por_contrato = {}

        conceptos = Conceptosfijos.objects.filter(
            conceptofijo__in=[
                'JORNADA MAXIMA MENSUAL',
                'HORA EXTRA DIURNA FACTOR',
                'HORA EXTRA NOCTURNA FACTOR',
                'HORA EXTRA DIURNA FESTIVA FACTOR',
                'HORA EXTRA NOCTURNA FESTIVA FACTOR',
                'RECARGO NOCTURNO FACTOR',
                'RECARGO DOMINICAL O FESTIVO FACTOR'
            ]
        ).values('conceptofijo', 'valorfijo')

        factores = {c['conceptofijo']: float(c['valorfijo']) for c in conceptos}

        jmm = factores.get('JORNADA MAXIMA MENSUAL', 1.0)
        hed_factor  = factores.get('HORA EXTRA DIURNA FACTOR', 1.0)
        hen_factor  = factores.get('HORA EXTRA NOCTURNA FACTOR', 1.0)
        hedf_factor = factores.get('HORA EXTRA DIURNA FESTIVA FACTOR', 1.0)
        henf_factor = factores.get('HORA EXTRA NOCTURNA FESTIVA FACTOR', 1.0)
        rn_factor   = factores.get('RECARGO NOCTURNO FACTOR', 1.0)
        rdf_factor  = factores.get('RECARGO DOMINICAL O FESTIVO FACTOR', 1.0)


        daily_regular = {}

        for t in tiempos_queryset:
            id_contrato = t.get('idcontrato_id')
            salario = Contratos.objects.get(idcontrato=id_contrato).salario

            fecha_ing = parse_date_obj(t.get('fechaingreso')) or parse_date_obj(t.get('fechasalida'))
            hora_ingreso = parse_time_obj(t.get('horaingreso'))
            hora_salida = parse_time_obj(t.get('horasalida'))
            horas_descuentos = horasdescuento_to_timedelta(t.get('horasdescuentos'))

            if not (hora_ingreso and hora_salida and fecha_ing):
                continue

            dt_ingreso = datetime.combine(fecha_ing, hora_ingreso)
            dt_salida = datetime.combine(fecha_ing, hora_salida)
            if dt_salida < dt_ingreso:
                dt_salida += timedelta(days=1)

            dt_salida_adj = dt_salida - horas_descuentos
            if dt_salida_adj < dt_ingreso:
                dt_salida_adj = dt_ingreso

            worked = dt_salida_adj - dt_ingreso
            if worked < timedelta():
                worked = timedelta()

            total_hours = round(worked.total_seconds() / 3600, 2)
            horas_normales = hed = hen = hedf = henf = rn = dyf = 0.0
            base_hours = 8.0
            hora_actual = dt_ingreso
            end_time = dt_salida_adj
            step = timedelta(minutes=1)

            while hora_actual < end_time:
                siguiente = min(hora_actual + step, end_time)
                dur = (siguiente - hora_actual).total_seconds() / 3600.0
                slice_date = hora_actual.date()
                is_festivo = slice_date in CO_HOLIDAYS or slice_date.weekday() == 6
                tipo = "diurna" if time(6, 0) <= hora_actual.time() < time(21, 0) else "nocturna"

                key_day = (id_contrato, slice_date)
                used_regular = daily_regular.get(key_day, 0.0)
                remaining_regular = max(0.0, base_hours - used_regular)

                if is_festivo:
                    dyf += dur
                    if tipo == "diurna":
                        hedf += dur
                    else:
                        henf += dur
                else:
                    if remaining_regular > 0:
                        alloc_regular = min(dur, remaining_regular)
                        if tipo == "diurna":
                            horas_normales += alloc_regular
                        else:
                            rn += alloc_regular
                        daily_regular[key_day] = used_regular + alloc_regular

                        rest = dur - alloc_regular
                        if rest > 0:
                            if tipo == "diurna":
                                hed += rest
                            else:
                                hen += rest
                    else:
                        if tipo == "diurna":
                            hed += dur
                        else:
                            hen += dur

                hora_actual = siguiente

            # 🔹 Acumular resultado por contrato
            if id_contrato not in horas_por_contrato:
                horas_por_contrato[id_contrato] = {
                    'salario': salario,
                    'horas_trabajadas': 0.0,
                    'horas_normales': 0.0,
                    'hed': 0.0,
                    'hen': 0.0,
                    'hedf': 0.0,
                    'henf': 0.0,
                    'rn': 0.0,
                    'dyf': 0.0,
                }

            horas_por_contrato[id_contrato]['horas_trabajadas'] += total_hours
            horas_por_contrato[id_contrato]['horas_normales'] += horas_normales
            horas_por_contrato[id_contrato]['hed'] += hed
            horas_por_contrato[id_contrato]['hen'] += hen
            horas_por_contrato[id_contrato]['hedf'] += hedf
            horas_por_contrato[id_contrato]['henf'] += henf
            horas_por_contrato[id_contrato]['rn'] += rn
            horas_por_contrato[id_contrato]['dyf'] += dyf 

        # 🔹 Calcular valores de pago por tipo de hora
        for contrato_id, valores in horas_por_contrato.items():
            salario = valores['salario']
            valor_hora = salario / jmm

            valores['Vhed']  = round(valores['hed']  * valor_hora * hed_factor, 1)
            valores['Vhen']  = round(valores['hen']  * valor_hora * hen_factor, 1)
            valores['Vhedf'] = round(valores['hedf'] * valor_hora * hedf_factor, 1)
            valores['Vhenf'] = round(valores['henf'] * valor_hora * henf_factor, 1)
            valores['Vrn']   = round(valores['rn']   * valor_hora * rn_factor, 1)
            valores['Vdyf']  = round(valores['horas_normales'] * valor_hora * rdf_factor, 1)  # recargo dominical opcional
            valores['dyf']  = round(valores['dyf'], 1)
            
            # 🔸 Total de valor de horas extras
            valores['ValorExtras'] = round(
                valores['Vhed'] + valores['Vhen'] + valores['Vhedf'] +
                valores['Vhenf'] + valores['Vrn'] + valores['Vdyf'], 1
            )

            # 🔹 Redondear
            for k, v in valores.items():
                if isinstance(v, (int, float)):
                    valores[k] = round(v, 1)

        return horas_por_contrato

    
    if selected_nomina_id:
        # Traer tiempos de la nómina seleccionada
        tiempos = Tiempos.objects.filter(idnomina=selected_nomina_id).select_related(
            'idcontrato', 'idcontrato__idempleado'
        ).annotate(
            nombre_completo=Concat(
                F('idcontrato__idempleado__papellido'),
                Value(' '),
                F('idcontrato__idempleado__sapellido'),
                Value(' '),
                F('idcontrato__idempleado__pnombre'),
                Value(' '),
                F('idcontrato__idempleado__snombre'),
                output_field=CharField()
            )
        ).order_by('-idmarcacion')
        value1 = True

    
    
            
        
    
    if accion == 'calcular':
        # Aquí puedes ejecutar una lógica especial
        value2 = True
        value1 = False
    
    # ---------- Lógica principal ----------
        if selected_nomina_id:
            try:
                nomina_sel = Crearnomina.objects.get(
                    idnomina=selected_nomina_id,
                    id_empresa_id=idempresa
                )
                if nomina_sel.fechainicial and nomina_sel.fechafinal:
                    tiempos_agregados = (
                        Tiempos.objects
                        .filter(
                            idempresa_id=idempresa,
                            fechaingreso__gte=nomina_sel.fechainicial,
                            fechaingreso__lte=nomina_sel.fechafinal
                        )
                        .values(
                            'idcontrato_id', 'horaingreso', 'horasalida',
                            'horasdescuentos', 'fechaingreso', 'fechasalida'
                        )
                    )

                    # Calculamos todas las horas
                    horas_por_contrato = calcular_horas_extras(tiempos_agregados)
                    
                    # Normalizamos a formato decimal
                    empleados_con_horas = []
                    for emp in empleados:
                        try:
                            emp_id = int(emp['idcontrato'])
                        except Exception:
                            emp_id = str(emp['idcontrato'])

                        data = horas_por_contrato.get(emp_id, {})
                        ## horas 
                        emp['horas_trabajadas'] = data.get('horas_trabajadas', 0)
                        emp['horas_normales'] = data.get('horas_normales', 0)
                        emp['hed'] = data.get('hed', 0)
                        emp['hen'] = data.get('hen', 0)
                        emp['hedf'] = data.get('hedf', 0)
                        emp['henf'] = data.get('henf', 0)
                        emp['rn'] = data.get('rn', 0)
                        
                        ## values 
                        emp['Vhed'] = data.get('Vhed', 0)
                        emp['Vhen'] = data.get('Vhen', 0)
                        emp['Vhedf'] = data.get('Vhedf', 0)
                        emp['Vhenf'] = data.get('Vhenf', 0)
                        emp['Vrn'] = data.get('Vrn', 0)
                        emp['Vdyf'] = data.get('Vdyf', 0)
                        emp['dyf'] = data.get('dyf', 0)
                        emp['ValorExtras'] = data.get('ValorExtras', 0)

                        if emp['horas_trabajadas'] > 0:
                            empleados_con_horas.append(emp)
                    empleados = empleados_con_horas
                    value2 = True

            except Crearnomina.DoesNotExist:
                pass
    
    
    if accion2 == 'grabar':
        
        value1 = False
        value2 = True
        value3 = True
        
        for data in empleados:
            contrato = Contratos.objects.get(idcontrato=data['idcontrato'])
            nomina = Crearnomina.objects.get(pk=selected_nomina_id)
            costo = Costos.objects.get(pk=contrato.idcosto.idcosto)
            empresa = Empresa.objects.get(pk=idempresa)

            print(data)
            # 🔹 Buscar o crear el registro
            obj, created = TiemposTotales.objects.update_or_create(
                idcontrato=contrato,
                idnomina=nomina,
                defaults={
                    'horasord':data.get('horas_normales', 0),
                    'horastrab':data.get('horas_trabajadas', 0),
                    'hed':data.get('hed', 0),
                    'vhed':data.get('Vhed', 0),
                    'hen':data.get('hen', 0),
                    'vhen':data.get('Vhen', 0),
                    'hedf':data.get('hedf', 0),
                    'vhedf':data.get('Vhedf', 0),
                    'henf':data.get('henf', 0),
                    'vhenf': data.get('Vhenf', 0),
                    'rn': data.get('rn', 0),
                    'vrn': data.get('Vrn', 0),
                    'dyf': data.get('dyf', 0),  
                    'vdyf': data.get('Vdyf', 0),
                    'valorextras': data.get('ValorExtras', 0),
                    'idcosto': costo,
                    'idempresa': empresa,
                }
            )
            print("Creado:", created, "→", obj)

        messages.success(request, 'Tiempos guardados correctamente')

        
    if accion2 == 'grabar2':
        value1 = value2 = value3 = False
        nomina = Crearnomina.objects.get(pk=selected_nomina_id)

        # 🔹 Cargar conceptos masivamente
        codigos = [3, 5, 6, 7, 8, 9, 16]
        conceptos = {
            c.codigo: c for c in Conceptosdenomina.objects.filter(codigo__in=codigos, id_empresa=idempresa)
        }

        faltantes = [c for c in codigos if c not in conceptos]
        if faltantes:
            messages.error(request, f"Faltan conceptos en la empresa: {faltantes}")
            return redirect(request.path)

        # 🔹 Relación campo ↔ concepto
        campos_a_concepto = {
            'hed': conceptos[5],
            'hen': conceptos[6],
            'dyf': conceptos[7],
            'hedf': conceptos[8],
            'henf': conceptos[9],
            'rn': conceptos[3],
            'rn_festivo': conceptos[16],
        }

        tiempos = TiemposTotales.objects.filter(idnomina_id=selected_nomina_id)

        for data in tiempos:
            for campo, concepto in campos_a_concepto.items():
                cantidad = getattr(data, campo, 0)
                valor_campo = f"v{campo}" if hasattr(data, f"v{campo}") else None
                valor = getattr(data, valor_campo, 0) if valor_campo else 0

                try:
                    # 🔸 Convertir y redondear a 2 decimales
                    cantidad = Decimal(cantidad).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    valor = Decimal(valor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                    # 🔸 Validar valores dentro de rango razonable
                    if cantidad > 0 and valor < Decimal('9999999999.99'):
                        Nomina.objects.update_or_create(
                            idcontrato=data.idcontrato,
                            idnomina=nomina,
                            idconcepto=concepto,
                            defaults={
                                'cantidad': cantidad,
                                'valor': valor,
                                'estadonomina': 1,
                            },
                        )
                        
                except (InvalidOperation, OverflowError) as e:
                    print(f"❌ Error numérico en contrato {data.idcontrato}: {e}")

        messages.success(request, "Tiempos aplicados correctamente a la nómina.")
        return redirect(reverse('payroll:payrollview', args=[selected_nomina_id]))

            
            
        
    return render(
        request,
        './payroll/time_list.html',
        {
            'tiempos': tiempos,
            'nominas': nominas,
            'true1': value1,
            'true2': value2,
            'true3': value3,
            'empleados': empleados,
            'selected_nomina_id': selected_nomina_id
        }
    )

@login_required
@role_required('accountant')
def time_edit(request,id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    tiempo = Tiempos.objects.get(idmarcacion = id)
    
    initial={
        'fechaingreso': tiempo.fechaingreso,
        'fechasalida': tiempo.fechasalida,
        'horaingreso': tiempo.horaingreso,
        'horasalida': tiempo.horasalida,
        'horasdescuentos': tiempo.horasdescuentos.hour if tiempo.horasdescuentos else 0,
        'contract': tiempo.idcontrato.idcontrato
    }
    
    form = TimeForm(idempresa = idempresa , initial = initial , id = id )
    
    if request.method == 'POST':
        form = TimeForm(request.POST , idempresa=idempresa , id = id)
        if form.is_valid():
            
            fechaingreso = form.cleaned_data['fechaingreso']
            fechasalida = form.cleaned_data['fechasalida']
            horaingreso = form.cleaned_data['horaingreso']
            horasalida = form.cleaned_data['horasalida']
            horasdescuentos = form.cleaned_data['horasdescuentos']
            
            if tiempo.fechaingreso != fechaingreso:
                tiempo.fechaingreso = fechaingreso 
            
            if tiempo.fechasalida != fechasalida:
                tiempo.fechasalida = fechasalida 
                
            if tiempo.horaingreso != horaingreso:
                tiempo.horaingreso = horaingreso 
                
            if tiempo.horasalida != horasalida:
                tiempo.horasalida = horasalida 
                
            if horasdescuentos is not None:
                nueva_hora = time(hour=int(horasdescuentos), minute=0)
                if tiempo.horasdescuentos != nueva_hora:
                    tiempo.horasdescuentos = nueva_hora

            
            tiempo.save()
            
            response = HttpResponse()
            response['X-Up-Accept-Layer'] = 'true'  #Indica a Unpoly que acepte (cierre) el modal
            response['X-Up-icon'] = 'success'  # URL para recargar la página principal   
            response['X-Up-message'] = 'Tiempo actualizado exitosamente'    
            
            params = {'datatipo': tiempo.idnomina.idnomina }
            url_base = reverse('payroll:time_list')  # genera algo como "/payroll/time/"
            url_completa = f"{url_base}?{urlencode(params)}"
            response['X-Up-Location'] = url_completa
            
            return response
        
    
    return render(
        request,
        './payroll/partials/time_edit.html',
        {'form': form}
    )



@login_required
@role_required('accountant')
def time_doc(request, id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    tiempos = Tiempos.objects.filter(idnomina=id).select_related('idcontrato__idsede')

    wb = Workbook()
    ws = wb.active
    ws.title = "Tiempo Marcados"

    headers = [
        'Idcontrato', 'empleado', 'Fechaingreso', 'Horaingreso', 'Fechasalida', 'Horasalida',
        'Horasdescuentos', 'Horastrab', 'Horasord', 'Saldo', 'Horasdomfes',
        'Hed', 'Hen', 'Hedf', 'Henf', 'Rn', 'Rnf', 'Dyf', 'Sede'
    ]
    ws.append(headers)

    # 🎨 Colores que se irán alternando (puedes añadir más)
    colors = [
        "FFF9C4",  # Amarillo claro
        "C8E6C9",  # Verde claro
        "BBDEFB",  # Azul claro
        "FFCDD2",  # Rojo rosado claro
        "D1C4E9",  # Lila claro
    ]

    current_contract = None
    color_index = 0

    # Recorremos los tiempos ordenados por contrato para que los bloques estén juntos
    for time in tiempos.order_by('idcontrato__idcontrato'):
        contrato_id = time.idcontrato.idcontrato

        # Si cambia de contrato, se cambia el color
        if contrato_id != current_contract:
            current_contract = contrato_id
            color_index = (color_index + 1) % len(colors)
            fill = PatternFill(start_color=colors[color_index], end_color=colors[color_index], fill_type="solid")

        # Escribimos la fila
        row = [
            contrato_id,
            'EMP Prueba',
            time.fechaingreso,
            time.horaingreso,
            time.fechasalida,
            time.horasalida,
            time.horasdescuentos,
            time.horasalida,
            time.horasalida,
            time.horasalida,
            time.horasalida,
            time.horasalida,
            time.horasalida,
            time.horasalida,
            time.horasalida,
            time.horasalida,
            time.horasalida,
            time.horasalida,
            time.idcontrato.idsede.nombresede if time.idcontrato.idsede else "",
        ]
        ws.append(row)

        # Aplicar color de fondo a toda la fila
        for cell in ws[ws.max_row]:
            cell.fill = fill

        # 🎯 Aplicar formato de fecha dd/mm/yyyy
        fecha_ingreso_cell = ws.cell(row=ws.max_row, column=3)
        fecha_salida_cell = ws.cell(row=ws.max_row, column=5)
        fecha_ingreso_cell.number_format = 'DD/MM/YYYY'
        fecha_salida_cell.number_format = 'DD/MM/YYYY'

    # Guardar en memoria y devolver como descarga
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=\"Tiempo_Marcados.xlsx\"'
    return response
    


def formatear_fecha(valor):
    if isinstance(valor, datetime):   # Si ya es datetime
        return valor.date()
    if isinstance(valor, str) and '/' in valor:
        try:
            return datetime.strptime(valor, '%d/%m/%Y').date()
        except:
            return valor
    return valor



def time_add(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario.get('idempresa')

    nominas = Crearnomina.objects.filter(
        estadonomina=True,
        id_empresa_id=idempresa
    ).order_by('-idnomina')

    if request.method == 'POST' and request.FILES.get('file'):
        errors = []
        file = request.FILES['file']
        idnomina = request.POST.get('idnomina')

        try:
            df = pd.read_csv(file, header=None,sep=";", encoding="utf-8")
        except Exception as e:
            errors.append(f"Error al leer el archivo: {str(e)}")
            return render(request, './companies/partials/disability_upload_errors.html', {'errors': errors})
        df = df.dropna(how="all")
        
        
        registros_validados = []

        for idx, fila in df.iterrows():
            try:
                contrato      = fila[0]
                fecha_ingreso = formatear_fecha(fila[1])
                fecha_salida  = formatear_fecha(fila[2])
                hora_ingreso  = fila[3]
                hora_salida   = fila[4]
                horas_descuentos  = fila[5]

                # --- Validaciones ---
                if not contrato:
                    errors.append(f"Fila {idx+1}: El contrato es obligatorio.")
                    continue

                if not fecha_ingreso:
                    errors.append(f"Fila {idx+1}: La fecha de ingreso no es válida.")
                    continue

                if fecha_salida and fecha_salida < fecha_ingreso:
                    errors.append(f"Fila {idx+1}: La fecha de salida no puede ser menor que la de ingreso.")
                    continue

                if not hora_ingreso or not hora_salida:
                    errors.append(f"Fila {idx+1}: Hora de ingreso y salida son obligatorias.")
                    continue

                empresa = Empresa.objects.get(idempresa =  idempresa )
                
                # Verificar que el contrato exista
                if not Contratos.objects.filter(idcontrato=contrato, id_empresa=idempresa).exists():
                    errors.append(f"Fila {idx+1}: El contrato {contrato} no existe en la empresa {empresa.nombreempresa}.")
                    continue

                # Evitar duplicados: contrato + fecha ingreso ya existente
                if Tiempos.objects.filter(idcontrato_id=contrato, fechaingreso=fecha_ingreso, idempresa_id=idempresa).exists():
                    errors.append(f"Fila {idx+1}: Ya existe un registro de tiempo para contrato {contrato} en la fecha {fecha_ingreso}.")
                    continue

                # Si pasa todas las validaciones, lo agregamos a lista
                registros_validados.append(
                    Tiempos(
                        fechaingreso=fecha_ingreso,
                        horaingreso=hora_ingreso,
                        idcontrato_id=contrato,
                        idnomina_id=idnomina,
                        fechasalida=fecha_salida,
                        horasalida=hora_salida,
                        horasdescuentos= horas_descuentos, 
                        idempresa_id=idempresa,
                    )
                )
            except Exception as e:
                errors.append(f"Fila {idx+1}: Error inesperado -> {str(e)}")

        # Si hubo errores: no se guarda nada
        if errors:
            return render(request, './companies/partials/disability_upload_errors.html', {
                'errors': errors
            })

        # Guardamos en bloque, asegurando atomicidad
        if registros_validados:
            with transaction.atomic():
                Tiempos.objects.bulk_create(registros_validados)
                return render(request, 'payroll/partials/success_time.html')

    return render(request, 'payroll/partials/time_add.html', {'nominas': nominas})




def time_data(request,id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    times = Tiempos.objects.filter(idempresa = idempresa ,idcontrato = id ).order_by('-fechaingreso') 
    
    return render(request, './payroll/partials/time_data.html', {'times': times})
