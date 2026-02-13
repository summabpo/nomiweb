from django.shortcuts import render
from apps.common.models import Nomina , NominaComprobantes ,Crearnomina , Contratos ,Empresa
from apps.components.humani import format_value
from io import BytesIO
from xhtml2pdf import pisa
from datetime import datetime
from apps.components.payrollgenerate import generate_summary
from apps.components.payrollgenerate import genera_comprobante 
from apps.components.mail import send_template_email3
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.units import cm
import time
from reportlab.pdfgen import canvas


def get_email_status(estado_email):
    if estado_email == 1:
        envio_email = 'Enviado'
    elif estado_email == 2:
        envio_email = 'Error'
    else:
        envio_email = 'Sin Enviar'

    return envio_email



@login_required
@role_required('company','accountant')
def payrollsheet_record(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    nominas = Crearnomina.objects.filter(estadonomina=False, id_empresa_id=idempresa).order_by('-idnomina')

    return render(request, 'companies/payrollsheetrecord.html', {
        'nominas': nominas,
    })


@login_required
@role_required('company','accountant')
def payrollsheet_record_date(request, id):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    empleados = Nomina.objects \
        .select_related('idcontrato') \
        .filter(idnomina=id) \
        .values(
            'idcontrato__idempleado__docidentidad', 'idcontrato__idempleado__papellido',
            'idcontrato__idempleado__pnombre', 'idcontrato__idempleado__snombre',
            'idcontrato__salario', 'idcontrato__idempleado__idempleado', 
            'idcontrato__idempleado__sapellido', 'idcontrato'
        ) \
        .order_by('idcontrato__idempleado__papellido') \
        .distinct()

    nombre = Crearnomina.objects.get(idnomina=id)
    # Inicializamos 'nomina' para cuando no se filtra
    nomina = Nomina.objects.filter(idnomina_id=id).order_by('idregistronom')
    
    return render(request, './companies/payrollsheet_record_date.html', {
        'nomina': nomina,
        'nombre':nombre,
        'empleados': empleados,
        'id': id
    })
    
    



@login_required
@role_required('company','accountant')
def payrollsheet(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    #nominas = Nomina.objects.select_related('idnomina').values('idnomina__nombrenomina', 'idnomina').distinct().order_by('-idnomina')
    #nominas = Nomina.objects.select_related('idnomina').values_list('idnomina__nombrenomina', 'idnomina').distinct().order_by('-idnomina')
    nominas = Crearnomina.objects.filter(id_empresa = idempresa , estadonomina = False ).values_list('nombrenomina', 'idnomina').order_by('-idnomina')
    compects = []
    acumulados = {}

    selected_nomina = request.GET.get('nomina')
    if selected_nomina:
        compectos = Nomina.objects.filter(idnomina=selected_nomina)
        
        # Consulta 1: Total neto
        # neto = Nomina.objects.filter(idnomina=id_nomina).aggregate(Sum('valor'))['valor__sum'] or 0
        # # Consulta 2: Total ingresos
        # ingresos = Nomina.objects.filter(idnomina=id_nomina, valor__gt=0).aggregate(Sum('valor'))['valor__sum'] or 0
        # descuentos = neto - ingresos
        # # Consulta 3: Salario básico
        # basico = Nomina.objects.filter(idnomina=id_nomina, idconcepto__in=[1, 4]).aggregate(Sum('valor'))['valor__sum'] or 0
        # # Consulta 4: Transporte
        # transporte = Nomina.objects.filter(idnomina=id_nomina, idconcepto=2).aggregate(Sum('valor'))['valor__sum'] or 0
        # # Consulta 5: Extras
        # extras = Nomina.objects.filter(idnomina=id_nomina, conceptosdenomina__extras=1).aggregate(Sum('valor'))['valor__sum'] or 0
        # otrosing = ingresos - basico - extras - transporte
        # # Consulta 6: Aportes
        # aportes = Nomina.objects.filter(idnomina=id_nomina, conceptosdenomina__aportess=1).aggregate(Sum('valor'))['valor__sum'] or 0
        # # Consulta 7: Préstamos
        # prestamos = Nomina.objects.filter(idnomina=id_nomina, idconcepto=50).aggregate(Sum('valor'))['valor__sum'] or 0
        # otrosdesc = descuentos - prestamos - aportes
        # # Consulta 8: Estado email
        # estado_email = CrearNomina.objects.filter(idnomina=id_nomina).values_list('envio_email', flat=True).first()
        
        
        for data in compectos:
            
            docidentidad = data.idcontrato.idcontrato
            try:
                comprobante = NominaComprobantes.objects.get(idnomina=selected_nomina, idcontrato=data.idcontrato.idcontrato, idcosto__idcosto=data.idcontrato.idcosto.idcosto)
            except NominaComprobantes.DoesNotExist:
                comprobante = None
                
                
            if docidentidad not in acumulados:
                acumulados[docidentidad] = {
                    'idcontrato': data.idcontrato.idcontrato,
                    'documento': data.idcontrato.idempleado.docidentidad ,
                    'nombre': f"{(data.idcontrato.idempleado.papellido or '')} {(data.idcontrato.idempleado.sapellido or '')} {(data.idcontrato.idempleado.pnombre or '')} {(data.idcontrato.idempleado.snombre or '')}",
                    'neto': 0,
                    'ingresos': 0,
                    'basico': 0,
                    'tpte': 0,
                    'extras': 0,
                    'aportess': 0,
                    'prestamos': 0,
                    'estado': get_email_status(comprobante.envio_email) if comprobante else None,
                    'nominaid': data.idnomina.idnomina,
                    'contratoid' :data.idcontrato.idcontrato,   
                }
            
            acumulados[docidentidad]['neto'] += data.valor
            acumulados[docidentidad]['ingresos'] += data.valor if data.valor > 0 else 0
            
            #acumulados[docidentidad]['basico'] += data.valor if data.idconcepto.sueldobasico == 1 else 0
            acumulados[docidentidad]['basico'] += data.valor if data.idconcepto.indicador.filter(nombre='sueldobasico').exists() else 0
            #acumulados[docidentidad]['tpte'] += data.valor if data.idconcepto.auxtransporte == 1 else 0
            acumulados[docidentidad]['tpte'] += data.valor if data.idconcepto.indicador.filter(nombre='auxtransporte').exists() else 0
            #acumulados[docidentidad]['extras'] += data.valor if data.idconcepto.extras == 1 else 0
            acumulados[docidentidad]['extras'] += data.valor if data.idconcepto.indicador.filter(nombre='extras').exists() else 0
            #acumulados[docidentidad]['aportess'] += data.valor if data.idconcepto.aportess == 1 else 0
            acumulados[docidentidad]['aportess'] += data.valor if data.idconcepto.indicador.filter(nombre='aportess').exists() else 0
            acumulados[docidentidad]['prestamos'] += data.valor if data.idconcepto.codigo == 50 else 0
            #acumulados[docidentidad]['prestamos'] += data.valor if data.idconcepto.indicador.filter(nombre='aportess').exists() else 0
        
        compects = list(acumulados.values())

    for compect in compects:
        compect['descuentos'] = compect['neto'] - compect['ingresos']
        compect['otrosing'] = compect['ingresos'] - compect['basico'] - compect['extras'] - compect['tpte']
        compect['otrosdesc'] = compect['descuentos'] - compect['prestamos'] - compect['aportess']
        
        # Formatear los valores
        for key in ['neto', 'ingresos', 'basico', 'tpte', 'extras', 'aportess', 'prestamos', 'descuentos', 'otrosing', 'otrosdesc']:
            compect[key] = format_value(compect[key])



    return render(request, 'companies/payrollsheet.html', {
        'nominas': nominas,
        'compects': compects,
        'selected_nomina': selected_nomina,
    })



def draw_watermark(p, width, height):
    """Dibuja la marca de agua diagonal 'Quote' en el centro de la página"""
    # Guardar el estado actual del canvas
    p.saveState()
    
    # Color más claro para la marca de agua (gris claro sutil pero visible)
    watermark_color = colors.HexColor("#D0D0D0")  # Gris claro más sutil
    p.setFillColor(watermark_color)
    
    # Configurar fuente muy grande y en negrita para mejor visibilidad
    font_size = 130  # Aumentado a 180 para que sea muy grande y visible
    p.setFont("Helvetica-Bold", font_size)
    
    # Calcular el centro de la página
    center_x = width / 2
    center_y = height / 2
    
    # Rotar el canvas 45 grados (diagonal)
    p.translate(center_x, center_y)
    p.rotate(45)
    
    # Dibujar el texto "Quote" centrado
    text = "Pre-nomina"
    text_width = p.stringWidth(text, "Helvetica-Bold", font_size)
    # Mejor cálculo del centro vertical (aproximadamente la mitad de la altura de la fuente)
    text_height_offset = font_size * 0.35  # Ajuste para centrar mejor verticalmente
    p.drawString(-text_width / 2, -text_height_offset, text)
    
    # Restaurar el estado del canvas
    p.restoreState()



@login_required
@role_required('company','accountant')
def generatepayrollsummary(request, idnomina, data):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    context = generate_summary(idnomina, idempresa , data )

    buffer = BytesIO()
    dark_blue = colors.HexColor("#1d2748")  # Primary dark blue
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Encabezado empresa
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(width / 2, height - 25, context['empresa'])
    p.setFont("Helvetica", 8)
    p.drawCentredString(width / 2, height - 35, context['nit'])
    p.drawCentredString(width / 2, height - 45, context['web'])

    
    p.setStrokeColor(colors.grey)
    p.setLineWidth(0.5)
    p.line(35, height - 60, width - 35, height - 60)

    if data == 0 :
        draw_watermark(p, width, height)

    try:
        logo = ImageReader(f"static/img/{context['logo']}")
        logo_width = 150
        logo_height = 50
        p.drawImage(logo, 35, height - 55, width=logo_width, height=logo_height,
                    preserveAspectRatio=True, mask='auto')
    except:
        pass

    # Subtítulo
    p.setFont("Courier-Bold", 15)
    p.drawCentredString(width / 2, height - 90, "Resumen de Nómina")
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width / 2, height - 110, context['nombre_nomina'])

    # ------------------ Tabla de grouped_nominas ------------------
    y = height - 140
    tabla_datos = [["Código", "Concepto", "Cantidad", "Ingresos", "Descuentos", "Neto"]]
    for item in context["grouped_nominas"]:
        fila = [
            item["idconcepto__codigo"],
            item["idconcepto__nombreconcepto"],
            str(item["cantidad_total"]),
            item["ingresos"],
            item["descuentos"],
            ' '
        ]
        tabla_datos.append(fila)

    tabla = Table(tabla_datos, colWidths=[1 * cm, 5 * cm, 2 * cm, 3 * cm, 3 * cm, 3 * cm])
    tabla.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
        ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
    ]))
    tabla_width, tabla_height = tabla.wrap(width, height)
    tabla.drawOn(p, 65, y - tabla_height)

    # ------------------ Tabla Totales al pie ------------------
    tabla_datos2 = [["", f"Total Empleados: {context['cantidad_empleados']}", "", context['total_ingresos'],
                     context['total_descuentos'], context['neto']]]

    tabla2 = Table(tabla_datos2, colWidths=[1 * cm, 5 * cm, 2 * cm, 3 * cm, 3 * cm, 3 * cm])
    tabla2.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
        ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
    ]))
    tabla2_width, tabla2_height = tabla2.wrap(width, height)
    tabla2_y = y - tabla_height - 20  # 20px espacio entre tablas
    tabla2.drawOn(p, 65, tabla2_y - tabla2_height)
    
    # Footer institucional
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.grey)
    p.drawCentredString(width / 2, 15, "Outsourcing de Nómina ::: www.nomiweb.co ::: Summa BPO SAS")

    # Finalizar
    p.setTitle(f"Resumen de Nómina {context['nombre_nomina']}")
    p.setAuthor("Nomiweb")
    p.setSubject("Resumen general de nómina")
    p.setCreator("Sistema Nomiweb")
    p.showPage()
    p.save()

    # Retornar response
    pdf = buffer.getvalue()
    buffer.close()
    nombre_archivo = f'Resumen_Nomina_{idnomina}.pdf'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
    response.write(pdf)
    return response



def draw_table(pdf, data, col_widths, y_pos, width, x_pos=22, row_height=20):
    tabla = Table(data, colWidths=col_widths, rowHeights=row_height)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b9c1c4")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    tabla.wrapOn(pdf, width, y_pos)
    tabla.drawOn(pdf, x_pos, y_pos - row_height)
    return y_pos - row_height

def build_payroll_certificate_pdf(pdf, context,data , logo=None):
    width, height = letter
    margin = 30
        
    # Logo y encabezado
    if logo:
        try:
            logo_width = 150
            logo_height = 50
            pdf.drawImage(logo, 35, height - 55, width=logo_width, height=logo_height,preserveAspectRatio=True, mask='auto')
            
        except Exception as e:
            print(f"[LOGO ERROR] No se pudo dibujar el logo: {e}")
            

    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(width / 2, height - 25, context['empresa'])
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(width / 2, height - 35, context['nit'])
    pdf.drawCentredString(width / 2, height - 45, context['web'])

    pdf.setStrokeColor(colors.grey)
    pdf.setLineWidth(0.5)
    pdf.line(35, height - 60, width - 35, height - 60)
    
    # Subtítulo
    pdf.setFont("Courier-Bold", 15)
    pdf.drawCentredString(width / 2, height - 90, "Comprobante de Nómina")
    
    y = height - 120
    # ---------------------- Tabla 1: Empleado ----------------------
    tabla1 = [
        ["Empleado", "Identificación", "Contrato", "Nómina"],
        [context['nombre_completo'], context['cc'], context['idcon'], context['idnomi']]
    ]

    tabla = Table(tabla1, colWidths=[8*cm, 4*cm, 4*cm, 4*cm], rowHeights=20)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b9c1c4")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    tabla.wrapOn(pdf, width, y)
    tabla.drawOn(pdf, 22, y - 40)
    y -= 40

    # ---------------------- Tabla 2: Cargo y salario ----------------------
    tabla2 = [
        ["Fecha Ingreso", "Cargo", "Salario", "Cuenta"],
        [context['fecha1'], context['cargo'], context['salario'], context['cuenta']]
    ]

    tabla = Table(tabla2, colWidths=[4*cm, 8*cm, 4*cm, 4*cm], rowHeights=20)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b9c1c4")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    tabla.wrapOn(pdf, width, y)
    tabla.drawOn(pdf, 22, y - 40)
    y -= 40

    # # ---------------------- Tabla 3: Costos y entidades ----------------------
    tabla3 = [
        ["Centro de Costo", "Periodo de Pago", "Salud", "Pensión"],
        [context['ccostos'], context['periodos'], str(context['eps']), str(context['pension'])]
    ]

    tabla = Table(tabla3, colWidths=[5*cm, 8*cm, 3.5*cm, 3.5*cm], rowHeights=20)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b9c1c4")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    tabla.wrapOn(pdf, width, y)
    tabla.drawOn(pdf, 22, y - 40)

    
    # # ---------------------- Tabla 4: Ingresos y Deducciones ----------------------
    
    encabezado_ingresos = [['INGRESOS', '', '', '']]
    filas_ingresos = []

    devengados = context['dataDevengado']
    for ingreso in devengados:
        fila = [
            ingreso.idconcepto.codigo,
            ingreso.nombreconcepto if ingreso else '',
            ingreso.cantidad if ingreso else '',
            f"{str(ingreso.valor).replace('.', ',')}" if ingreso else '',
        ]
        filas_ingresos.append(fila)

    # Rellenar hasta 15 filas (sin contar el encabezado)
    while len(filas_ingresos) < 15:
        filas_ingresos.append(['', '', '', ''])

    tabla_ingresos = encabezado_ingresos + filas_ingresos

    # DEDUCCIONES
    encabezado_descuentos = [['DEDUCCIONES', '', '', '']]
    filas_descuentos = []

    descuentos = context['dataDescuento']
    for descuento in descuentos:
        fila = [
            descuento.idconcepto.codigo,
            descuento.nombreconcepto if descuento else '',
            descuento.cantidad if descuento else '',
            f"{str(descuento.valor).replace('.', ',')}" if descuento else '',
        ]
        filas_descuentos.append(fila)

    # Rellenar hasta 15 filas
    while len(filas_descuentos) < 15:
        filas_descuentos.append(['', '', '', ''])

    tabla_descuentos = encabezado_descuentos + filas_descuentos

    # Columnas
    col_widths = [1*cm, 5*cm, 1.5*cm, 2.5*cm]
    

    # Crear tablas
    table_ingresos = Table(tabla_ingresos, colWidths=col_widths)
    table_descuentos = Table(tabla_descuentos, colWidths=col_widths)

    # Estilo común
        
    estilo_tabla = TableStyle([
        ('SPAN', (0, 0), (-1, 0)),
        # Encabezado gris claro sin colores si prefieres: eliminalo
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b9c1c4")),
        
        ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # Alineación general
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),# Alinear concepto a la izquierda
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),# Alinear cantidad a la derecha
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'), # Alinear valor a la derecha

        # Si no quieres ninguna línea ni color:
        # (simplemente omite las siguientes líneas o comenta)
        ('LINEBEFORE', (1, 0), (-1, -1), 0.5, colors.black),
        ('LINEAFTER', (0, 0), (-2, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
    ])
    table_ingresos.setStyle(estilo_tabla)
    table_descuentos.setStyle(estilo_tabla)

    # Posiciones
    w_i, h_i = table_ingresos.wrap(0, 0)
    w_d, h_d = table_descuentos.wrap(0, 0)

    bottom_y = height - 250
    table_ingresos.drawOn(pdf, x=22, y=bottom_y - h_i)
    table_descuentos.drawOn(pdf, x=306, y=bottom_y - h_d)

    if data == 0 :
        draw_watermark(pdf, width, height)
    
    # ---------------------- Tabla 5: Totales ----------------------

    tabla5 = [
        ['', f"Total Ingresos:", '', context['sumadataDevengado'], '', f"Total Deducciones: ", '', context['sumadataDescuento']],
        ['', 'Total a Pagar:', '', context['total'], '', '', '', '']
    ]

    col_widths = [1*cm, 5*cm, 1*cm, 3*cm, 1*cm, 5*cm, 1*cm, 3*cm]
    

    tabla = Table(tabla5, colWidths=col_widths, rowHeights=18)

    tabla.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.8, colors.black),

        # Encabezado con spans bien colocado
        # Colores
        ('BACKGROUND', (0, 0), (3, 0), colors.HexColor("#b9c1c4")),
        ('BACKGROUND', (4, 0), (7, 0), colors.HexColor("#b9c1c4")),
        ('BACKGROUND', (0, -1), (2, -1), colors.HexColor("#81DAF5")),

        ('FONTNAME', (0, 0), (-1, 1), 'Courier-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        
        
        ('ALIGN', (3, 0), (3, 0), 'RIGHT'),  # sumadataDevengado
        ('ALIGN', (7, 0), (7, 0), 'RIGHT'),  # sumadataDescuento
        ('ALIGN', (3, 1), (3, 1), 'RIGHT'),  # total
    
    ]))

    tabla.wrapOn(pdf, width, y)
    tabla.drawOn(pdf, 22, y - 390)
    # Footer institucional
    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(colors.grey)
    pdf.drawCentredString(width / 2, 15, "Outsourcing de Nómina ::: www.nomiweb.co ::: Summa BPO SAS")



@login_required
@role_required('company', 'accountant')
def generatepayrollsummary2(request, idnomina,data=None):


    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    empresa_data = Empresa.objects.get(idempresa=idempresa)
    if data == 0 : 
        contratos = Nomina.objects.filter(idnomina=idnomina ,estadonomina = 1).order_by('idcontrato__idempleado__papellido').values_list('idcontrato', flat=True).distinct()
    else:
        contratos = Nomina.objects.filter(idnomina=idnomina ,estadonomina = 2).order_by('idcontrato__idempleado__papellido').values_list('idcontrato', flat=True).distinct()
    # Precargar logo solo una vez
    
    logo = None
    try:
        logo_path = f"static/img/{empresa_data.logo}"
        logo = ImageReader(logo_path)
    except Exception as e:
        print(f"[LOGO ERROR] No se pudo cargar el logo: {e}")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    for i, idcontrato in enumerate(contratos, start=1):
        t0 = time.time()
        context = genera_comprobante(idnomina, idcontrato,data)        # Generar la página individual
        build_payroll_certificate_pdf(pdf, context, data, logo)
        pdf.showPage()  # Agrega una nueva página
    
    nombre_archivo = f'Certificado_{idnomina}_{datetime.now().strftime("%Y-%m-%d")}.pdf'
    
    pdf.setTitle(nombre_archivo)
    pdf.setAuthor("Nomiweb")
    pdf.setSubject(f"Comprobante de Nomina_{idnomina}_{datetime.now().strftime('%Y-%m-%d')}")
    pdf.setCreator("Sistema Nomiweb")
    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
    return response


@login_required
@role_required('company', 'accountant')
def generatepayrollcertificate(request, idnomina, idcontrato,data=None):
    context = genera_comprobante(idnomina, idcontrato,data)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    # Encabezado empresa
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(width / 2, height - 25, context['empresa'])
    p.setFont("Helvetica", 8)
    p.drawCentredString(width / 2, height - 35, context['nit'])
    p.drawCentredString(width / 2, height - 45, context['web'])

    # Línea horizontal
    p.setStrokeColor(colors.grey)
    p.setLineWidth(0.5)
    p.line(35, height - 60, width - 35, height - 60)

    # Logo
    try:
        logo = ImageReader(f"static/img/{context['logo']}")
        logo_width = 150
        logo_height = 50
        p.drawImage(logo, 35, height - 55, width=logo_width, height=logo_height,
                    preserveAspectRatio=True, mask='auto')
    except:
        pass

    # Subtítulo
    p.setFont("Courier-Bold", 15)
    p.drawCentredString(width / 2, height - 90, "Comprobante de Nómina")

    y = height - 120
# ---------------------- Tabla 1: Empleado ----------------------
    tabla1 = [
        ["Empleado", "Identificación", "Contrato", "Nómina"],
        [context['nombre_completo'], context['cc'], context['idcon'], context['idnomi']]
    ]

    tabla = Table(tabla1, colWidths=[8*cm, 4*cm, 4*cm, 4*cm], rowHeights=20)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b9c1c4")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    tabla.wrapOn(p, width, y)
    tabla.drawOn(p, 22, y - 40)
    y -= 40

    # ---------------------- Tabla 2: Cargo y salario ----------------------
    tabla2 = [
        ["Fecha Ingreso", "Cargo", "Salario", "Cuenta"],
        [context['fecha1'], context['cargo'], context['salario'], context['cuenta']]
    ]

    tabla = Table(tabla2, colWidths=[4*cm, 8*cm, 4*cm, 4*cm], rowHeights=20)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b9c1c4")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    tabla.wrapOn(p, width, y)
    tabla.drawOn(p, 22, y - 40)
    y -= 40

    # # ---------------------- Tabla 3: Costos y entidades ----------------------
    tabla3 = [
        ["Centro de Costo", "Periodo de Pago", "Salud", "Pensión"],
        [context['ccostos'], context['periodos'], str(context['eps']), str(context['pension'])]
    ]

    tabla = Table(tabla3, colWidths=[5*cm, 8*cm, 3.5*cm, 3.5*cm], rowHeights=20)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b9c1c4")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    tabla.wrapOn(p, width, y)
    tabla.drawOn(p, 22, y - 40)



    # # ---------------------- Tabla 4: Ingresos y Deducciones ----------------------
    
    encabezado_ingresos = [['INGRESOS', '', '', '']]
    filas_ingresos = []

    devengados = context['dataDevengado']
    for ingreso in devengados:
        fila = [
            ingreso.idconcepto.codigo,
            ingreso.nombreconcepto if ingreso else '',
            ingreso.cantidad if ingreso else '',
            f"{str(ingreso.valor).replace('.', ',')}" if ingreso else '',
        ]
        filas_ingresos.append(fila)

    # Rellenar hasta 15 filas (sin contar el encabezado)
    while len(filas_ingresos) < 15:
        filas_ingresos.append(['', '', '', ''])

    tabla_ingresos = encabezado_ingresos + filas_ingresos

    # DEDUCCIONES
    encabezado_descuentos = [['DEDUCCIONES', '', '', '']]
    filas_descuentos = []

    descuentos = context['dataDescuento']
    for descuento in descuentos:
        fila = [
            descuento.idconcepto.codigo,
            descuento.nombreconcepto if descuento else '',
            descuento.cantidad if descuento else '',
            f"{str(descuento.valor).replace('.', ',')}" if descuento else '',
        ]
        filas_descuentos.append(fila)

    # Rellenar hasta 15 filas
    while len(filas_descuentos) < 15:
        filas_descuentos.append(['', '', '', ''])

    tabla_descuentos = encabezado_descuentos + filas_descuentos

    # Columnas
    col_widths = [1*cm, 5*cm, 1.5*cm, 2.5*cm]

    # Crear tablas
    table_ingresos = Table(tabla_ingresos, colWidths=col_widths)
    table_descuentos = Table(tabla_descuentos, colWidths=col_widths)

    # Estilo común
        
    estilo_tabla = TableStyle([
        ('SPAN', (0, 0), (-1, 0)),
        # Encabezado gris claro sin colores si prefieres: eliminalo
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b9c1c4")),
        
        ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # Alineación general
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),# Alinear concepto a la izquierda
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),# Alinear cantidad a la derecha
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'), # Alinear valor a la derecha

        # Si no quieres ninguna línea ni color:
        # (simplemente omite las siguientes líneas o comenta)
        ('LINEBEFORE', (1, 0), (-1, -1), 0.5, colors.black),
        ('LINEAFTER', (0, 0), (-2, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
    ])
    table_ingresos.setStyle(estilo_tabla)
    table_descuentos.setStyle(estilo_tabla)

    # Posiciones
    w_i, h_i = table_ingresos.wrap(0, 0)
    w_d, h_d = table_descuentos.wrap(0, 0)

    bottom_y = height - 250
    table_ingresos.drawOn(p, x=22, y=bottom_y - h_i)
    table_descuentos.drawOn(p, x=306, y=bottom_y - h_d)
    

    # ---------------------- Tabla 5: Totales ----------------------

    tabla5 = [
        ['', f"Total Ingresos:", '', context['sumadataDevengado'], '', f"Total Deducciones: ", '', context['sumadataDescuento']],
        ['', 'Total a Pagar:', '', context['total'], '', '', '', '']
    ]

    col_widths = [1*cm, 5*cm, 1*cm, 3*cm, 1*cm, 5*cm, 1*cm, 3*cm]

    tabla = Table(tabla5, colWidths=col_widths, rowHeights=18)

    tabla.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.8, colors.black),

        # Encabezado con spans bien colocado
        # Colores
        ('BACKGROUND', (0, 0), (3, 0), colors.HexColor("#b9c1c4")),
        ('BACKGROUND', (4, 0), (7, 0), colors.HexColor("#b9c1c4")),
        ('BACKGROUND', (0, -1), (2, -1), colors.HexColor("#81DAF5")),

        ('FONTNAME', (0, 0), (-1, 1), 'Courier-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        
        
        ('ALIGN', (3, 0), (3, 0), 'RIGHT'),  # sumadataDevengado
        ('ALIGN', (7, 0), (7, 0), 'RIGHT'),  # sumadataDescuento
        ('ALIGN', (3, 1), (3, 1), 'RIGHT'),  # total
    
    ]))

    tabla.wrapOn(p, width, y)
    tabla.drawOn(p, 22, y - 390)
    
    
    # Footer institucional
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.grey)
    p.drawCentredString(width / 2, 15, "Outsourcing de Nómina ::: www.nomiweb.co ::: Summa BPO SAS")


    ## data unica 
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    nombre_archivo = f'Certificado_{context["cc"]}_{fecha_actual}.pdf'
    
    # Finalizar PDF
    p.showPage()
    p.setTitle(nombre_archivo)
    p.setAuthor("Nomiweb")
    p.setSubject("Comprobante de Nomina {context['cc']}")
    p.setCreator("Sistema Nomiweb")
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
    response.write(pdf)
    return response



""" 
para el optimo funcionamiento del views , es requerido que se borre el icono 1 
se cambie la configuracion de correos electronicos y se cree la plantilla 

icono 1 : [:5] - linea 145 
icono 2 : recipient_list - entre la linea 152 - 158
icono 3 :  success, message - linea 177

"""

@login_required
@role_required('company','accountant')
def massive_mail(request, idnomina):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    data = 10
    
    
    cantiok = cantifal = cont = error = 0     
    enviados = False
    errores = []
    
    compectos = (
        Nomina.objects
        .filter(idnomina = idnomina)
        .select_related('idcontrato__idempleado')  # optimiza consultas
        .order_by('idcontrato')
        .distinct('idcontrato')
    )

    for data in compectos:
        cont += 1  # total de contratos revisados
        try:
            email = data.idcontrato.idempleado.email
            if email and email.strip():   # existe y no está vacío
                cantiok += 1
            else:
                cantifal += 1
        except Exception:
            # Por si idempleado viene null o hay dato corrupto
            error += 1
            cantifal += 1

    ## post de envio masivo 
    

    if request.method == 'POST':
        enviados = False
        modo = request.POST.get('modo')
        compectos = Nomina.objects.filter(idnomina = idnomina ).distinct('idcontrato')

        for comp in compectos: 
            try:
                datacn = NominaComprobantes.objects.get(idnomina_id = idnomina ,idcontrato_id = comp.idcontrato )
            except NominaComprobantes.DoesNotExist:
                datacn = None
                contrato = Contratos.objects.get(idcontrato_id = comp.idcontrato) 
            
            empresa_data = Empresa.objects.get(idempresa=idempresa)
            logo = None
            try:
                logo_path = f"static/img/{empresa_data.logo}"
                logo = ImageReader(logo_path)
            except Exception as e:
                print(f"[LOGO ERROR] No se pudo cargar el logo: {e}")
                
            
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)

            context = genera_comprobante(idnomina, comp.idcontrato_id ,data) 
            build_payroll_certificate_pdf(pdf, context, data, logo)
            pdf.showPage() 
            nombre_archivo = f'Certificado_{idnomina}_{datetime.now().strftime("%Y-%m-%d")}.pdf'
            
            pdf.setTitle(nombre_archivo)
            pdf.setAuthor("Nomiweb")
            pdf.setSubject(f"Comprobante de Nomina_{idnomina}_{datetime.now().strftime('%Y-%m-%d')}")
            pdf.setCreator("Sistema Nomiweb")
            pdf.save()
            buffer.seek(0)
                
            # Enviar el PDF por correo
            email_subject = 'Tu Comprobante de Nòmina'
                
            #recipient_list = ['mikepruebas@yopmail.com']  # Lista de destinatarios
            recipient_list = [context["mail"]]

            attachment = {
                'filename': nombre_archivo,
                'content': buffer.getvalue(), 
                'mimetype': 'application/pdf'
            }
            
            email_sent, error_msg = send_template_email3(
                email_type='nomina1',
                context=context,
                subject=email_subject,
                recipient_list=recipient_list,
                attachment=attachment
            )
                        
                        

            if not email_sent:
                enviados = False
                errores.append(f'Error al enviar el correo a {context["nombre_completo"]}: {error_msg} ')
            else :
                enviados = True
                            
            
            #email_status = 'Correo enviado exitosamente.' if email_sent else 'Error al enviar el correo. : '
            
            if datacn :
                pass
            else :
                NominaComprobantes.objects.create(
                    idcontrato = contrato, 
                    salario = contrato.salario, 
                    cargo = contrato.cargo.nombrecargo, 
                    idcosto_id = contrato.idcosto.idcosto , 
                    salud = contrato.salario ,
                    idnomina_id = idnomina ,
                    envio_email = 2
                    )
                datacn = NominaComprobantes.objects.get(idnomina_id = idnomina ,idcontrato = comp )

            if email_sent :
                datacn.envio_email = 1
                datacn.save()
            else:
                datacn.envio_email = 2
                datacn.save()

        
    
    
    
        
        
    
    context = {
        'selected_nomina' : idnomina,
        "cantiok": cantiok,
        "cantifal": cantifal,
        "total": cont,
        "errores":errores,
        "enviados":enviados,
    }
    
    return render(request, './companies/partials/massive_mail.html', context )



@login_required
@role_required('company','accountant')
def unique_mail(request, idnomina, idcontrato):
    if request.method == 'POST':
        # Obtener tu objeto
        
        
        # RETORNAR HTML del nuevo estado (¡NO JSON!)
        html = render_to_string('partials/estado_botones.html', {
            'compect': obj
        })
        return HttpResponse(html)
    
    return HttpResponse('Método no permitido', status=405)


# @login_required
# @role_required('company','accountant')
# def unique_mail(request,idnomina,idcontrato):
#     usuario = request.session.get('usuario', {})
#     idempresa = usuario['idempresa']
#     data = 10
    
#     try:
#         datacn = NominaComprobantes.objects.get(idnomina_id = idnomina ,idcontrato_id = idcontrato )
#     except NominaComprobantes.DoesNotExist:
#         datacn = None
#         contrato = Contratos.objects.get(idcontrato = idcontrato)
    
#     empresa_data = Empresa.objects.get(idempresa=idempresa)
#     logo = None
#     try:
#         logo_path = f"static/img/{empresa_data.logo}"
#         logo = ImageReader(logo_path)
#     except Exception as e:
#         print(f"[LOGO ERROR] No se pudo cargar el logo: {e}")
        
    
#     buffer = BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=letter)

#     context = genera_comprobante(idnomina, idcontrato,data) 
#     build_payroll_certificate_pdf(pdf, context, logo)
#     pdf.showPage() 
#     nombre_archivo = f'Certificado_{idnomina}_{datetime.now().strftime("%Y-%m-%d")}.pdf'
    
#     pdf.setTitle(nombre_archivo)
#     pdf.setAuthor("Nomiweb")
#     pdf.setSubject(f"Comprobante de Nomina_{idnomina}_{datetime.now().strftime('%Y-%m-%d')}")
#     pdf.setCreator("Sistema Nomiweb")
#     pdf.save()
#     buffer.seek(0)

#     # Enviar el PDF por correo
#     email_subject = 'Tu Comprobante de Nòmina'
    
#     #
#     recipient_list = ['manuel.david.13.b@gmail.com']  # Lista de destinatarios
#     #recipient_list = [context["mail"],'mikepruebas@yopmail.com']
    
#     attachment = {
#         'filename': nombre_archivo,
#         'content': buffer.getvalue(),
#         'mimetype': 'application/pdf'
#     }

#     email_sent = send_template_email3(
#         email_type='nomina1',  # Ajusta el tipo de correo según corresponda
#         context=context,
#         subject=email_subject,
#         recipient_list=recipient_list,
#         attachment=attachment
#     )

#     email_status = 'Correo enviado exitosamente.' if email_sent else 'Error al enviar el correo.'
    
#     if datacn :
#         pass
#     else :
#         NominaComprobantes.objects.create(
#             idcontrato = contrato, 
#             salario = contrato.salario, 
#             cargo = contrato.cargo.nombrecargo, 
#             idcosto_id = contrato.idcosto.idcosto , 
#             salud = contrato.salario ,
#             idnomina_id = idnomina ,
#             envio_email = 2
#             )
#         datacn = NominaComprobantes.objects.get(idnomina_id = idnomina ,idcontrato_id = idcontrato )
        

#     if email_sent :
#         datacn.envio_email = 1
#         datacn.save()
#     else:
#         datacn.envio_email = 2
#         datacn.save()
    
#     response_data = {
#             'message': 'ID recibido correctamente',
#             'status' : email_status,
#             'name' : context["nombre_completo"] ,
#             'pass' :email_sent
#         }
    
#     print(response_data)
    
#     return JsonResponse(response_data)

