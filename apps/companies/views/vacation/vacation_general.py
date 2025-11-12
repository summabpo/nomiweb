from django.shortcuts import render, redirect, get_object_or_404
from apps.components.decorators import  role_required
from apps.common.models  import Anos ,Tipodenomina, Vacaciones ,Contratos ,Crearnomina ,Nomina , Conceptosdenomina
from django.http import JsonResponse
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from io import BytesIO
from xhtml2pdf import pisa
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from apps.components.datacompanies import datos_cliente
from reportlab.lib import colors
from reportlab.lib.units import cm
from django.urls import reverse
from django.http import HttpResponse
from apps.payroll.views.payroll.payroll_automatic_systems import calcular_vacaciones
from django.utils import timezone
from datetime import date
from django.db.models import F, Case, When, Value, DateField

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
@role_required('company','accountant')
def vacation_general(request):
    """
    Vista que muestra una lista general de empleados activos con contrato para la empresa actual,
    con el propósito de gestionar vacaciones.

    Requiere que el usuario esté autenticado y tenga el rol de 'company' o 'accountant'.

    Recupera los contratos activos de empleados pertenecientes a la empresa del usuario actual,
    formatea correctamente los nombres para evitar valores None, y los pasa al contexto de la plantilla.

    Template renderizado: './companies/vacation_general.html'

    Contexto:
        - contratos_empleados (list): Lista de diccionarios con la información del empleado y su contrato.

    Returns:
        HttpResponse: Página renderizada con los datos de los empleados.
    """
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    # Obtener la lista de empleados activos
    contratos_empleados = (
        Contratos.objects
        .select_related('idempleado')
        .filter(
            estadocontrato=1,
            tipocontrato__idtipocontrato__in=[1, 2, 3, 4],
            id_empresa_id=idempresa
        )
        .values(
            'idempleado__docidentidad',
            'idempleado__sapellido',
            'idempleado__papellido',
            'idempleado__pnombre',
            'idempleado__snombre',
            'idempleado__idempleado',
            'idcontrato'
        )
    )

    # Limpiar nombres: eliminar None y "no data"
    for emp in contratos_empleados:
        for campo in [
            'idempleado__pnombre',
            'idempleado__snombre',
            'idempleado__papellido',
            'idempleado__sapellido'
        ]:
            valor = emp.get(campo)
            if valor is None or str(valor).strip().lower() == 'no data':
                emp[campo] = ''
    
    context = {
        'contratos_empleados': contratos_empleados,
    }
    
    return render(request, './companies/vacation_general.html', context)



@login_required
@role_required('company', 'accountant')
def vacation_resumen(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    vacaciones = (
        Vacaciones.objects.filter(
            idcontrato__id_empresa=idempresa,
            tipovac__idvac__in=[1, 2]
        )
        .annotate(
            fecha_orden=Case(
                When(fechainicialvac__isnull=False, then=F('fechainicialvac')),
                When(fechapago__isnull=False, then=F('fechapago')),
                default=Value(None),
                output_field=DateField()
            )
        )
        .values(
            "idcontrato__idempleado__docidentidad",
            "idcontrato__idempleado__papellido",
            "idcontrato__idempleado__sapellido",
            "idcontrato__idempleado__pnombre",
            "idcontrato__idempleado__snombre",
            "idcontrato",
            "fechainicialvac",
            "fechapago",
            "tipovac__nombrevacaus",
            "idvacaciones",
            "fecha_orden",
            "idvacmaster",
        )
        .order_by('-fecha_orden')
    )
    
    # Limpiar los valores "no data" y None
    vacaciones = [
        {
            k: (
                "" if (v is None or str(v).strip().lower() == "no data") 
                else v
            )
            for k, v in vac.items()
        }
        for vac in vacaciones
    ]
    
    context = {
        'vacaciones': vacaciones
    }
    
    return render(request, './companies/vacation_resumen.html', context)


@login_required
@role_required('company', 'accountant')
def vacation_resumen_send(request, id):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    nominas = Crearnomina.objects.filter(estadonomina=True, id_empresa_id=idempresa).order_by('-idnomina')
    if request.method == 'POST':
        ahora = timezone.localtime(timezone.now())
        hoy = date.today()
        
        # 🔹 Recuperar valores del formulario
        nueva_nomina_flag = request.POST.get('nueva_nomina') == 'on'
        id_nomina = request.POST.get('nomina')

        nomina_final = None

        # 🔹 Caso 1: crear nueva nómina automática
        if nueva_nomina_flag:
            nomina_final = Crearnomina.objects.create(
                nombrenomina=f"Nomina Aut. Vacas - {ahora.strftime('%Y-%m-%d %H:%M:%S')}",
                fechainicial=hoy,
                fechafinal=hoy,
                fechapago=ahora.date(),
                tiponomina=Tipodenomina.objects.get(tipodenomina='Vacaciones'),
                mesacumular= MES_CHOICES[ahora.month][0] if ahora.month else '',
                anoacumular=Anos.objects.get(ano=ahora.year),
                estadonomina=True,
                diasnomina=1,
                id_empresa_id=idempresa,
            )

        # 🔹 Caso 2: si no se marca crear nueva nómina
        else:
            if id_nomina:
                nomina_final = Crearnomina.objects.filter(
                    idnomina=id_nomina, id_empresa_id=idempresa
                ).first()

            # Validar: si no existe la nómina seleccionada → crear una nueva automática
            if not nomina_final:
                nomina_final = Crearnomina.objects.create(
                    nombrenomina=f"Nomina Aut. Vacas - {ahora.strftime('%Y-%m-%d %H:%M:%S')}",
                    fechainicial=hoy,
                    fechafinal=hoy,
                    fechapago=ahora.date(),
                    tiponomina=Tipodenomina.objects.get(tipodenomina='Vacaciones'),
                    mesacumular= MES_CHOICES[ahora.month][0] if ahora.month else '',
                    anoacumular=Anos.objects.get(ano=ahora.year),
                    estadonomina=True,
                    diasnomina=1,
                    id_empresa_id=idempresa,
                )

        Calculo_vacaciones_por_id(idnomina=nomina_final.idnomina, idvacaciones=id )

        
        response = HttpResponse('', content_type='text/html; charset=utf-8')
        response['X-Up-Accept-Layer'] = 'true'
        response['X-Up-Location'] = reverse('companies:vacation_resumen')
        response['X-Up-Message'] = 'Vacaciones enviadas correctamente a la nómina.'
        response['X-Up-Icon'] = 'success'       
        return response
    
    return render(request, './companies/partials/vacation_resumen_send.html',{'id':id , 'nominas':nominas})



def Calculo_vacaciones_por_id(idnomina, idvacaciones):
    # 🔹 Obtener nómina y datos base
    nomina_actual = Crearnomina.objects.get(idnomina=idnomina)
    vaca = Vacaciones.objects.get(idvacaciones=idvacaciones)
    contrato = vaca.idcontrato

    # 🔹 Determinar tipo de vacaciones
    tipo = vaca.tipovac.idvac  # 1: disfrutadas, 2: compensadas
    if tipo == 1:
        concepto = Conceptosdenomina.objects.get(codigo=24, id_empresa=contrato.id_empresa_id)
    elif tipo == 2:
        concepto = Conceptosdenomina.objects.get(codigo=32, id_empresa=contrato.id_empresa_id)
    else:
        print(f'Tipo de vacaciones no reconocido para {vaca.idvacaciones}')
        return

    # 🔹 Evitar duplicados
    if Nomina.objects.filter(
        idnomina=idnomina,
        idconcepto=concepto,
        control=vaca.idvacaciones
    ).exists():
        print(f'Vacación {vaca.idvacaciones} ya está en la nómina.')
        return

    # ==========================================================
    # 🟨 CASO ESPECIAL: NÓMINA AUTOMÁTICA DE VACACIONES
    # ==========================================================
    if nomina_actual.nombrenomina.startswith('Nomina Aut. Vacas'):
        print(f"Procesando vacación {vaca.idvacaciones} en nómina automática (sin validación de rango).")

        if tipo == 1:  # Disfrutadas
            dias_vacaciones = (vaca.ultimodiavac - vaca.fechainicialvac).days + 1
            valor = (contrato.salario / 30) * dias_vacaciones
            cantidad = dias_vacaciones

        elif tipo == 2:  # Compensadas
            dias_vacaciones = vaca.diasvac or 0
            base = vaca.basepago or contrato.salario
            valor = (base / 30) * dias_vacaciones
            cantidad = dias_vacaciones
            if vaca.pagovac:
                valor = vaca.pagovac

        Nomina.objects.create(
            idconcepto=concepto,
            cantidad=cantidad,
            estadonomina=1,
            valor=valor,
            idcontrato=contrato,
            idnomina_id=idnomina,
            control=vaca.idvacaciones
        )
        return 0

    # ==========================================================
    # 🟦 CASO NORMAL: NÓMINAS REGULARES (VALIDAR RANGO)
    # ==========================================================
    if tipo == 1 and vaca.fechainicialvac and vaca.ultimodiavac:
        if vaca.fechainicialvac <= nomina_actual.fechafinal and vaca.ultimodiavac >= nomina_actual.fechainicial:
            inicio = max(vaca.fechainicialvac, nomina_actual.fechainicial)
            fin = min(vaca.ultimodiavac, nomina_actual.fechafinal)
            dias_vacaciones = (fin - inicio).days + 1
            valor = (contrato.salario / 30) * dias_vacaciones
            cantidad = calcular_vacaciones(contrato, nomina_actual)
        else:
            print(f'Vacación {vaca.idvacaciones} fuera del rango de nómina.')
            return

    elif tipo == 2 and vaca.fechapago:
        if nomina_actual.fechainicial <= vaca.fechapago <= nomina_actual.fechafinal:
            dias_vacaciones = vaca.diasvac or 0
            base = vaca.basepago or contrato.salario
            valor = (base / 30) * dias_vacaciones
            cantidad = 1
            if vaca.pagovac:
                valor = vaca.pagovac
        else:
            print(f'Vacación {vaca.idvacaciones} (tipo 2) fuera del rango de nómina.')
            return
    else:
        print(f'Vacación {vaca.idvacaciones} sin datos válidos.')
        return

    # Crear registro
    Nomina.objects.create(
        idconcepto=concepto,
        cantidad=cantidad,
        estadonomina=1,
        valor=valor,
        idcontrato=contrato,
        idnomina_id=idnomina,
        control=vaca.idvacaciones
    )


    return 0


@login_required
@role_required('company', 'accountant')
def vacation_resumen_doc(request, id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    context = generate_vacation_doc(idempresa, id)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- Encabezado empresa ---
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(width / 2, height - 25, context['empresa'])
    p.setFont("Helvetica", 8)
    p.drawCentredString(width / 2, height - 35, context['nit'])
    p.drawCentredString(width / 2, height - 45, context['web'])

    p.setStrokeColor(colors.grey)
    p.setLineWidth(0.5)
    p.line(35, height - 60, width - 35, height - 60)

    try:
        logo = ImageReader(f"static/img/{context['logo']}")
        p.drawImage(logo, 35, height - 55, width=150, height=50, preserveAspectRatio=True, mask='auto')
    except:
        pass

    # --- Subtítulo ---
    p.setFont("Helvetica-Bold", 15)
    p.drawCentredString(width / 2, height - 90, "Liquidación de Vacaciones")

    # --- Bloque de datos del empleado ---
    y = height - 120
    x_label = 60
    x_value = 240
    line_height = 15

    
    # 'documento': empleado_doc,
    # 'cargo': cargo,
    # 'fechacontrato': fechacontrato,
    # 'pago': pago,
    
    datos = [
        ("Empleado:", context.get('empleado') or "---"),
        ("Documento de Id.:", context.get('documento') or "---"),
        ("Cargo:", context.get('cargo') or "---"),
        ("Fecha de Ingreso:", context.get('fechacontrato') or "---"),
        ("Fecha de Pago:", context.get('pago') or "---"),
    ]

    for label, value in datos:
        p.setFont("Courier", 12)
        p.drawString(x_label, y, label)

        p.setFont("Courier-Bold", 10)
        p.drawString(x_value, y, str(value))
        y -= line_height

    # Línea separadora
    p.setStrokeColor(colors.grey)
    p.line(35, y - 10, width - 35, y - 10)
    y -= 40  # espacio antes de tabla

    # --- Construcción de tabla ---
    vaca = [
        [
            item.tipovac.nombrevacaus if item.tipovac else '',
            item.fechainicialvac.strftime('%Y-%m-%d') if item.fechainicialvac else '',
            item.ultimodiavac.strftime('%Y-%m-%d') if item.ultimodiavac else '',
            item.diascalendario,
            item.diasvac,
            f"${item.pagovac:,.0f}" if item.pagovac else '',
            item.perinicio or '',
            item.perfinal or ''
        ]
        for item in context["vacaciones"]
    ]
    
    
    table_data = [
        ["Tipo", "Inicio", "Fin", "Días Cal.", "Días Vac.", "Valor Vac.", "Per. Inicio", "Per. Fin"]
    ] + vaca

    table = Table(table_data, colWidths=[115, 65, 65, 60, 60, 80, 65,65])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONT', (0, 0), (-1, 0), 'Courier-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONT', (0, 1), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))

    # Medir altura de la tabla antes de dibujarla
    table_width, table_height = table.wrapOn(p, width, height)

    # Si no cabe en la página, crea una nueva
    if y - table_height < 50:
        p.showPage()
        y = height - 100

    table.drawOn(p, 20, y - table_height)

    # --- Footer institucional ---
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.grey)
    p.drawCentredString(width / 2, 20, "Outsourcing de Nómina ::: www.nomiweb.co ::: Summa BPO SAS")

    # --- Finalizar documento ---
    p.setAuthor("Nomiweb")
    p.setSubject("Resumen general de nómina")
    p.setCreator("Sistema Nomiweb")
    p.showPage()
    p.save()

    # --- Retornar respuesta ---
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="liquidacion_de_vacaciones_{id}.pdf"'
    response.write(pdf)
    return response





def generate_vacation_doc(idempresa, id):
    # Obtener datos del cliente
    datac = datos_cliente(idempresa)
    vaca_qs = Vacaciones.objects.filter(idvacmaster=id , tipovac__idvac__in=[1, 2])

    # Tomar el primer registro de vacaciones (si existe)
    vaca_obj = vaca_qs.first()

    empleado_nombre = ""
    empleado_doc = ""
    cargo = ""
    fechacontrato = ""
    pago = ""

    
    if vaca_obj and vaca_obj.idcontrato:
        contrato = vaca_obj.idcontrato

        # Datos del empleado
        if contrato.idempleado:
            empleado = contrato.idempleado
            empleado_nombre = " ".join(
                part.strip()
                for part in [empleado.pnombre, empleado.snombre, empleado.papellido, empleado.sapellido]
                if part and part.strip().lower() != "no data"
            ).strip()
            empleado_doc = empleado.docidentidad or ""

        # Datos del contrato
        cargo = getattr(contrato.cargo, 'nombrecargo', '') or ''
        fechacontrato = getattr(contrato, 'fechainiciocontrato', '') or ''
        
        pago = vaca_obj.fechapago  or '---'  # o el campo que uses como fecha de pago

        
    context = {
        'empresa': datac.get('nombreempresa', ''),
        'nit': datac.get('nit', ''),
        'web': datac.get('website', ''),
        'logo': datac.get('logo', ''),
        'vacaciones': vaca_qs,
        'empleado': empleado_nombre,
        'documento': empleado_doc,
        'cargo': cargo,
        'fechacontrato': fechacontrato,
        'pago': pago,
    }
    
    return context



@login_required
@role_required('company','accountant')
def vacation_resumen_data(request,id):
    
    
    vacaciones = Vacaciones.objects.get(idvacaciones=id)
    
    
    context = {
        'vacaciones' : vacaciones
    }
    
    return render(request, './companies/partials/vacation_resumen_data.html', context)


@login_required
@role_required('company', 'accountant')
def absences_resumen(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    vacaciones = Vacaciones.objects.filter(
        idcontrato__id_empresa=idempresa, 
        tipovac__idvac__in=[3, 4, 5]
    ).values(
        "idcontrato__idempleado__docidentidad",
        "idcontrato__idempleado__papellido",
        "idcontrato__idempleado__sapellido",
        "idcontrato__idempleado__pnombre",
        "idcontrato__idempleado__snombre",
        "idcontrato",
        "idvacaciones",
    ).order_by('-idvacaciones')
    
    # Limpiar "no data" y valores nulos
    vacaciones = [
        {
            k: (
                "" if (v is None or str(v).strip().lower() == "no data")
                else v
            )
            for k, v in vac.items()
        }
        for vac in vacaciones
    ]
    
    context = {
        'vacaciones': vacaciones
    }
    
    return render(request, './companies/absences_resumen.html', context)

@login_required
@role_required('company','accountant')
def absences_resumen_data(request,id):
    
    
    vacaciones = Vacaciones.objects.get(idvacaciones=id)
        
    context = {
        'vacaciones' : vacaciones
    }
    
    return render(request, './companies/partials/vacation_resumen_data.html', context)



@login_required
@role_required('company', 'accountant')
def absences_resumen_send(request, id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    nominas = Crearnomina.objects.filter(estadonomina=True, id_empresa_id=idempresa).order_by('-idnomina')
    
    if request.method == 'POST':
        ahora = timezone.localtime(timezone.now())
        hoy = date.today()
        
        # 🔹 Recuperar valores del formulario
        nueva_nomina_flag = request.POST.get('nueva_nomina') == 'on'
        id_nomina = request.POST.get('nomina')

        nomina_final = None

        # 🔹 Caso 1: crear nueva nómina automática
        if nueva_nomina_flag:
            nomina_final = Crearnomina.objects.create(
                nombrenomina=f"Nomina Aut. Ausen - {ahora.strftime('%Y-%m-%d %H:%M:%S')}",
                fechainicial=hoy,
                fechafinal=hoy,
                fechapago=ahora.date(),
                tiponomina=Tipodenomina.objects.get(tipodenomina='Vacaciones'),
                mesacumular= MES_CHOICES[ahora.month][0] if ahora.month else '',
                anoacumular=Anos.objects.get(ano=ahora.year),
                estadonomina=True,
                diasnomina=1,
                id_empresa_id=idempresa,
            )

        # 🔹 Caso 2: si no se marca crear nueva nómina
        else:
            if id_nomina:
                nomina_final = Crearnomina.objects.filter(
                    idnomina=id_nomina, id_empresa_id=idempresa
                ).first()

            # Validar: si no existe la nómina seleccionada → crear una nueva automática
            if not nomina_final:
                nomina_final = Crearnomina.objects.create(
                    nombrenomina=f"Nomina Aut. Ausen - {ahora.strftime('%Y-%m-%d %H:%M:%S')}",
                    fechainicial=hoy,
                    fechafinal=hoy,
                    fechapago=ahora.date(),
                    tiponomina=Tipodenomina.objects.get(tipodenomina='Vacaciones'),
                    mesacumular= MES_CHOICES[ahora.month][0] if ahora.month else '',
                    anoacumular=Anos.objects.get(ano=ahora.year),
                    estadonomina=True,
                    diasnomina=1,
                    id_empresa_id=idempresa,
                )
                

            # 🔹 Obtener datos de la vacación
            vaca = Vacaciones.objects.get(idvacaciones=id)

            # ✅ Validar rango de fechas
            if not (
                nomina_final.fechainicial <= vaca.fechainicialvac <= nomina_final.fechafinal and
                nomina_final.fechainicial <= vaca.ultimodiavac <= nomina_final.fechafinal
            ):
                response = HttpResponse('', content_type='text/html; charset=utf-8')
                response['X-Up-Accept-Layer'] = 'true'
                response['X-Up-Location'] = reverse('companies:absences_resumen')
                response['X-Up-Message'] = 'Las fechas de las vacaciones no están dentro del rango de la nómina seleccionada.'
                response['X-Up-Icon'] = 'warning'
                return response
                
                # response = HttpResponse('', content_type='text/html; charset=utf-8')
                # response['X-Up-Accept-Layer'] = 'true'
                # response['X-Up-Message'] = (
                #     'Las fechas de las vacaciones no están dentro del rango de la nómina seleccionada.'
                # )
                # response['X-Up-Icon'] = 'warning'
                # return response

            # 🔹 Crear registros en la nómina (si pasa la validación)
            concepto1 = Conceptosdenomina.objects.get(codigo=31, id_empresa_id=idempresa)
            concepto2 = Conceptosdenomina.objects.get(codigo=83, id_empresa_id=idempresa)

            Nomina.objects.create(
                idconcepto=concepto1,
                cantidad=vaca.diascalendario,
                estadonomina=1,
                valor=vaca.pagovac,
                idcontrato=vaca.idcontrato,
                idnomina=nomina_final,
                control=vaca.idvacaciones
            )

            Nomina.objects.create(
                idconcepto=concepto2,
                cantidad=vaca.diascalendario,
                estadonomina=1,
                valor=-(vaca.pagovac),
                idcontrato=vaca.idcontrato,
                idnomina=nomina_final,
                control=vaca.idvacaciones
            )

            # 🔹 Respuesta final OK
            response = HttpResponse('', content_type='text/html; charset=utf-8')
            response['X-Up-Accept-Layer'] = 'true'
            response['X-Up-Location'] = reverse('companies:absences_resumen')
            response['X-Up-Message'] = 'Vacaciones enviadas correctamente a la nómina.'
            response['X-Up-Icon'] = 'success'
            return response
    
    
    return render(request, './companies/partials/absences_resumen_send.html',{'id':id , 'nominas':nominas})


@login_required
@role_required('company','accountant')
def get_novedades(request):
    """
    API View que retorna las novedades de tipo 'Vacaciones' o 'Ausencias/licencias no remuneradas'
    asociadas a un contrato específico en formato JSON.

    Requiere autenticación y rol de 'company' o 'accountant'.

    Parámetros GET:
        - tipo (str): Tipo de novedad a consultar ('Vacaciones' o cualquier otro para ausencias/licencias).
        - idcontrato (int): ID del contrato del cual se desean consultar las novedades.

    Returns:
        JsonResponse: Diccionario que contiene el nombre completo del empleado y una lista de novedades,
                      cada una con datos como fecha de inicio, último día, días calendario, días de vacaciones,
                      pago, periodo de inicio y fin, y ID de la novedad.

    Estructura del JSON:
    {
        "nombre_empleado": "Nombre Apellido",
        "novedades": [
            {
                "novedad": "Tipo de novedad",
                "fecha_inicial": "YYYY-MM-DD",
                "ultimo_dia": "YYYY-MM-DD",
                "dias_cal": "X",
                "dias_vac": "X",
                "pago": "XXX.XX",
                "periodo_ini": "YYYY-MM-DD",
                "periodo_fin": "YYYY-MM-DD",
                "id": X
            },
            ...
        ]
    }
    """
    tipo_novedad = request.GET.get('tipo', '')  
    idcontaro = request.GET.get('idcontrato', '')  
    # Obtenemos el contrato y el nombre del empleado relacionado
    contrato = Contratos.objects.filter(idcontrato=idcontaro).first()
    nombre_empleado = f" {contrato.idempleado.papellido}  {contrato.idempleado.sapellido} {contrato.idempleado.pnombre}  {contrato.idempleado.snombre} " 

    # Inicializamos la estructura de datos con el nombre del empleado
    data = {
        "nombre_empleado": nombre_empleado,
        "novedades": []  # Aquí almacenaremos las novedades
    }

    if tipo_novedad == 'Vacaciones':
        vacaciones = Vacaciones.objects.filter(idcontrato__idcontrato=idcontaro, tipovac__idvac__in=[1,2]) 
        for vacacion in vacaciones:
            novedad = {
                "novedad": vacacion.tipovac.nombrevacaus if vacacion.tipovac and vacacion.tipovac.nombrevacaus else '',
                "fecha_inicial": vacacion.fechainicialvac.strftime('%Y-%m-%d') if vacacion.fechainicialvac else '',
                "ultimo_dia": vacacion.ultimodiavac.strftime('%Y-%m-%d') if vacacion.ultimodiavac else '',
                "dias_cal": vacacion.diascalendario if vacacion.diascalendario is not None else '0',
                "dias_vac": vacacion.diasvac if vacacion.diasvac is not None else '0',
                "pago": str(vacacion.pagovac) if vacacion.pagovac is not None else '0',
                "periodo_ini": vacacion.perinicio.strftime('%Y-%m-%d') if vacacion.perinicio else '',
                "periodo_fin": vacacion.perfinal.strftime('%Y-%m-%d') if vacacion.perfinal else '',
                "id": vacacion.idvacaciones
            }
            data["novedades"].append(novedad)
            
    else:  # Asumimos 'ausencias' o 'licencias no remuneradas'
        vacaciones = Vacaciones.objects.filter(idcontrato__idcontrato=idcontaro, tipovac__idvac__in=[3,4,5]) 
        for vacacion in vacaciones:
            novedad = {
                "novedad": vacacion.tipovac.nombrevacaus if vacacion.tipovac and vacacion.tipovac.nombrevacaus else '',
                "fecha_inicial": vacacion.fechainicialvac.strftime('%Y-%m-%d') if vacacion.fechainicialvac else '',
                "ultimo_dia": vacacion.ultimodiavac.strftime('%Y-%m-%d') if vacacion.ultimodiavac else '',
                "dias_cal": vacacion.diascalendario if vacacion.diascalendario is not None else '0',
                "dias_vac": vacacion.diasvac if vacacion.diasvac is not None else '0',
                "pago": str(vacacion.pagovac) if vacacion.pagovac is not None else '0',
                "periodo_ini": vacacion.perinicio.strftime('%Y-%m-%d') if vacacion.perinicio else '',
                "periodo_fin": vacacion.perfinal.strftime('%Y-%m-%d') if vacacion.perfinal else '',
                "id": vacacion.idvacaciones
            }
            data["novedades"].append(novedad)
            
    return JsonResponse(data, safe=False)

