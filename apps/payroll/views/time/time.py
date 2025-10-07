from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Tiempos , Crearnomina , Contratos , Empresa
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

@login_required
@role_required('accountant')
def time_list(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    nominas = Crearnomina.objects.filter(
        estadonomina=True,
        id_empresa_id=idempresa
    ).order_by('-idnomina')

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

    selected_nomina_id = request.GET.get('datatipo')

    empleados = [
        {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': ' '.join(filter(None, [
                contrato['idempleado__papellido'] if contrato['idempleado__papellido'] != 'no data' else '',
                contrato['idempleado__sapellido'] if contrato['idempleado__sapellido'] != 'no data' else '',
                contrato['idempleado__pnombre'] if contrato['idempleado__pnombre'] != 'no data' else '' ,
                contrato['idempleado__snombre'] if contrato['idempleado__snombre'] != 'no data' else ''
            ])),
            'idcontrato': contrato['idcontrato'],
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
                        'idcontrato_id','horaingreso','horasalida',
                        'horasdescuentos','fechaingreso','fechasalida'
                    )
                )

                horas_por_contrato = {}
                for t in tiempos_agregados:
                    raw_id = t.get('idcontrato_id')
                    try:
                        id_contrato = int(raw_id)
                    except Exception:
                        id_contrato = str(raw_id)

                    fecha = parse_date_obj(t.get('fechaingreso')) or parse_date_obj(t.get('fechasalida')) or date.today()
                    hora_ingreso = parse_time_obj(t.get('horaingreso'))
                    hora_salida = parse_time_obj(t.get('horasalida'))
                    horas_descuentos = horasdescuento_to_timedelta(t.get('horasdescuentos'))

                    if hora_ingreso and hora_salida:
                        dt_ingreso = datetime.combine(fecha, hora_ingreso)
                        dt_salida = datetime.combine(fecha, hora_salida)

                        if dt_salida < dt_ingreso:
                            dt_salida += timedelta(days=1)

                        worked = dt_salida - dt_ingreso - horas_descuentos
                        if worked < timedelta():
                            worked = timedelta()

                        horas_por_contrato[id_contrato] = horas_por_contrato.get(id_contrato, timedelta()) + worked

                # normalizamos a horas decimales (keys normalmente int)
                horas_por_contrato_decimal = {
                    k: round(v.total_seconds() / 3600, 2) for k, v in horas_por_contrato.items()
                }

                # asignar horas y filtrar solo empleados con horas > 0 (horas extras)
                empleados_con_horas = []
                for emp in empleados:
                    try:
                        emp_id = int(emp['idcontrato'])
                    except Exception:
                        emp_id = str(emp['idcontrato'])
                    horas = horas_por_contrato_decimal.get(emp_id, 0)
                    emp['horas_trabajadas'] = horas
                    if horas > 0:
                        empleados_con_horas.append(emp)

                # reemplazamos la lista original por la filtrada
                empleados = empleados_con_horas
                print(empleados)
        except Crearnomina.DoesNotExist:
            pass

    return render(
        request,
        './payroll/time_list.html',
        {
            'empleados': empleados,
            'nominas': nominas,
            'selected_nomina_id': selected_nomina_id
        }
    )
def formatear_fecha(valor):
    if isinstance(valor, datetime):   # Si ya es datetime
        return valor.date()
    if isinstance(valor, str) and '/' in valor:
        try:
            return datetime.strptime(valor, '%d/%m/%Y').date()
        except:
            return valor
    return valor

def es_domingo(fecha_str):
    fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
    return fecha.weekday() == 6  # En Python, lunes=0, domingo=6

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
                horas_extras  = fila[5]

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
