from django.shortcuts import render
from apps.common.models  import Liquidacion
from io import BytesIO
from xhtml2pdf import pisa
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
from apps.components.settlementgenerator import settlementgenerator
from apps.components.humani import format_value

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import os








@login_required
@role_required('company','accountant')
def settlementlist(request):
    """
    Vista para listar las liquidaciones de contrato realizadas en una empresa.

    Esta vista recupera todas las liquidaciones asociadas a la empresa del usuario actual, las ordena por identificador 
    y aplica formato a los valores monetarios (cesantías, intereses, prima, vacaciones y total de liquidación) antes de enviarlos al template.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene la sesión del usuario autenticado, incluyendo el ID de la empresa.

    Returns
    -------
    HttpResponse
        Renderiza el template 'companies/settlementlist.html' con la lista de liquidaciones disponibles para la empresa.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol 'company' o 'accountant' para acceder a esta vista.
    Los valores monetarios se formatean con la función `format_value` antes de ser enviados al template.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    liquidaciones = Liquidacion.objects.filter(idcontrato__id_empresa = idempresa ).order_by('idliquidacion')
    
    
    for compect in liquidaciones:
        # Accede a los atributos del modelo usando la notación de punto
        compect.cesantias = format_value(compect.cesantias)
        compect.intereses = format_value(compect.intereses)
        compect.prima = format_value(compect.prima)
        compect.vacaciones = format_value(compect.vacaciones)
        compect.totalliq = format_value(compect.totalliq)
    
    return render(request, 'companies/settlementlist.html',{
        'liquidaciones':liquidaciones,
    } )



def settlementlistdownload(request,idliqui):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    context = settlementgenerator(idliqui,idempresa)

    # Datos simulados (reemplazar por queryset)
    empleado = context['nombre_completo']
    documento =  context['cc']
    cargo = context['cargo']
    fecha_ingreso = context['ingreso']
    fecha_terminacion = context['terminación'] # Pendiente
    tipo_contrato = context['tipoc']
    causa = context['causa']
    salario = context['salario']
    suspension = context['sus']

    conceptos = [
        [item["concepto"], item["base"], item["dias"], item["valor"]]
        for item in context["data"]
    ]
    
    
    conceptos2 = [
        ["Recargo Nocturno", " ", " 4.0", "14.970"],
        ["Hora Extra Diurna", " ", "2.5", "33.415"],
        ["Hora Extra Nocturna", " ", "4.0", "74.850"],
        ["Dominical / Festivo", " ", "8.0", "149.700"],
        ["EPS", " ", "0.0", "-10.917"],
        ["AFP", " ", "0.0", "-10.917"],
    ]
    
    total = context['total']

    texto_legal = f"""
    <para align="justify">
    1. Que el empleador ha pagado la totalidad de los valores correspondientes a salarios, horas extras, descansos compensatorios, trabajos suplementarios, cesantías, intereses de cesantías, vacaciones, prima de servicios, auxilio de transporte, y en sí, todo concepto relacionado con salarios, prestaciones o indemnizaciones causadas en la relación laboral 
    2. Que con el pago del dinero anotado en la presente liquidación, queda transada cualquier diferencia relativa al contrato de trabajo extinguido, o a cualquier diferencia anterior. Por lo tanto, esta transacción tiene como efecto la terminación de las obligaciones provenientes de la relación laboral que existió entre {context['empresa']} y el trabajador, quienes declaran estar a paz y salvo por todo concepto.
    A la entrega de esta liquidación también certifico que he recibido una orden para practicarme el examen médico de egreso y una copia del último pago de aportes a la seguridad social.
    </para>
    """


    # Crear PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título principal
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
        logo_width = 150
        logo_height = 50
        p.drawImage(
            logo,
            35,                             
            height - 55, 
            width=logo_width,
            height=logo_height,
            preserveAspectRatio=True,
            mask='auto'
        )
    except:
        pass


    # Subtítulo
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width / 2, height - 90, "Liquidación de Contrato de Trabajo")

    # Posiciones iniciales
    y = height - 120
    x_label = 60
    x_value = 240
    line_height = 15

    # Datos en forma de tupla (etiqueta, valor)
    datos = [
        ("Empleado:", empleado),
        ("Documento de Id.:", documento),
        ("Cargo:", cargo),
        ("Fecha de Ingreso:", fecha_ingreso),
        ("Fecha de Terminación:", fecha_terminacion),
        ("Tipo de Contrato:", tipo_contrato),
        ("Causa de Liquidación:", causa),
        ("Salario:", salario),
        ("Suspensión/Lic. N. R.:", suspension),
    ]

    # Dibujo
    for label, value in datos:
        p.setFont("Courier", 12)
        p.drawString(x_label, y, label)

        p.setFont("Courier-Bold", 12)
        p.drawString(x_value, y, str(value))

        y -= line_height
    
    
    p.setStrokeColor(colors.grey)
    p.setLineWidth(0.5)
    p.line(35, height - 260, width - 35, height - 260)
    
    # Tabla de liquidación
    table_data = [["CONCEPTO", "BASE", "DIAS", "VALOR A PAGAR"]] + conceptos
    table = Table(table_data, colWidths=[180, 100, 100, 140])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        #('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        
        ('FONT', (0, 0), (-1, 0), 'Courier-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),     # CONCEPTO → izquierda
        ('ALIGN', (1, 1), (3, -1), 'RIGHT'),    # BASE, DIAS, VALOR → derecha
        
        
        ('FONT', (0, 1), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 9)
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 45, y - 100)

    # Total
    p.setFont("Courier-Bold", 10)
    p.drawString(320, y - 120, f"TOTAL PRESTACIONES:       ${total}")

        
    p.setStrokeColor(colors.grey)
    p.setLineWidth(0.5)
    p.line(35, height - 530, width - 35, height - 530)
    
    # Texto legal con Paragraph
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontSize = 9
    style.leading = 14
    paragraph = Paragraph(texto_legal, style)
    paragraph.wrapOn(p, width - 120, 200)
    paragraph.drawOn(p, 60, y - 400)

    # Firma del empleado
    
    p.setStrokeColor(colors.grey)
    p.setLineWidth(0.5)
    p.line(350, 65, width - 60 , 65)
    
    p.setFont("Helvetica-Bold", 10)
    p.drawString(370, 50, empleado)

    # Footer institucional
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.grey)
    p.drawCentredString(width / 2, 15, "Outsourcing de Nómina ::: www.nomiweb.co ::: Summa BPO SAS")

    # Finalizar PDF
    
    

    p.setTitle(f"Certificado de Liquidación - {empleado}")
    p.setAuthor("Nomiweb")
    p.setSubject("Liquidación de Contrato de Trabajo")
    p.setCreator("Sistema Nomiweb")
    
    p.showPage()
    p.save()
    
    nombre_archivo = f'Certificado_Liquidacion_{empleado}.pdf'
    
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
    response.write(pdf)
    return response




# @login_required
# @role_required('company','accountant')
# def settlementlistdownload2(request,idliqui):

#     usuario = request.session.get('usuario', {})
#     idempresa = usuario['idempresa']
    
#     context = settlementgenerator(idliqui,idempresa)

#     html_string = render(request, './html/liquidacion.html', context).content.decode('utf-8')
    
#     fecha_actual = datetime.now().strftime('%Y-%m-%d')
    
#     pdf = BytesIO()
#     pisa_status = pisa.CreatePDF(html_string, dest=pdf)
#     pdf.seek(0)

#     if pisa_status.err:
#         return HttpResponse('Error al generar el PDF', status=400)
    
#     nombre_archivo = f'Certificado_{context["cc"]}_{fecha_actual}.pdf'

#     response = HttpResponse(pdf, content_type='application/pdf')
#     response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
    
#     return response
    
