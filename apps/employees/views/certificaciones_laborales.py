from django.shortcuts import render,redirect

from io import BytesIO
from django.http import HttpResponse

## agregadas por manuel 
from io import BytesIO
from xhtml2pdf import pisa
from apps.components.workcertificategenerator import workcertificategenerator , workcertificatedownload
from django.contrib import messages
from apps.common.models import  Certificaciones , Contratos
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle, Paragraph
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.units import cm
import time
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.lib.styles import getSampleStyleSheet

def get_empleado_name(empleado):
    papellido = empleado.get('idempleado__papellido', '') if empleado.get('idempleado__papellido') is not None else ""
    sapellido = empleado.get('idempleado__sapellido', '') if empleado.get('idempleado__sapellido') is not None else ""
    pnombre = empleado.get('idempleado__pnombre', '') if empleado.get('idempleado__pnombre') is not None else ""
    snombre = empleado.get('idempleado__snombre', '') if empleado.get('idempleado__snombre') is not None else ""
    return f"{papellido} {sapellido} {pnombre} {snombre}"


@login_required
@role_required('employee')
def vista_certificaciones(request):
    """
    Muestra al empleado una vista interactiva para gestionar sus certificaciones laborales.

    Esta vista permite al usuario seleccionar un contrato y ver las certificaciones asociadas. 
    Según el estado del contrato (activo o terminado), se cargan opciones diferentes para generar certificados.
    También se formatea la información para presentarla de manera clara en la interfaz.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP del navegador. Contiene la sesión del usuario y parámetros GET.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'employees/certificaciones_laborales.html' con los datos del contrato y certificaciones.

    See Also
    --------
    Certificaciones : Modelo que representa los certificados laborales generados.
    Contratos : Modelo que contiene información sobre los contratos del empleado.
    get_empleado_name : Función auxiliar para formatear el nombre completo del empleado.

    Notes
    -----
    - Solo accesible para empleados autenticados.
    - Si el empleado tiene un solo contrato, se selecciona automáticamente.
    - Se ajustan las opciones del select según si el contrato está activo o liquidado.
    - Los valores de salario se formatean en estilo colombiano (puntos como separador de miles).
    """

    usuario = request.session.get('usuario', {})
    select_data = {}
    ESTADOS_CONTRATO = {
        1: "ACTIVO",
        2: "TERMINADO"
    }
    
    ide = usuario['idempleado']
    selected_empleado = request.GET.get('contrato')
    lista_certificaciones = []
    select = None
    
    
    # contratos
    contratos_sin = Contratos.objects.filter(idempleado__idempleado=ide)    
    contratos = []
    
    for con in contratos_sin:
        estado_contrato = ESTADOS_CONTRATO.get(con.estadocontrato, "")
        fechafincontrato = f"{con.fechafincontrato}" if con.fechafincontrato is not None else ""
        contrato = {
            'cc': f"{con.cargo} - {con.fechainiciocontrato} {estado_contrato} {fechafincontrato}",
            'idcontrato': con.idcontrato
        }
        
        contratos.append(contrato)
    
    cont = len(contratos)
    
    if cont == 1 : 
        selected_empleado = contratos[0]['idcontrato']    
    
    if selected_empleado:
        auxcontrato = Contratos.objects.filter(idcontrato=selected_empleado).values('estadocontrato')
        if auxcontrato.exists():
            estado_contrato = auxcontrato[0]['estadocontrato']
            
            if estado_contrato == 1:
                select_data = {
                    '1': 'Con salario básico',
                    '2': 'Con salario promedio',
                    '3': 'Sin salario',
                }
            elif estado_contrato == 2:
                select_data = {
                    '4': 'Contrato Liquidado',
                }
            else:
                select_data = {}
        
        
            select = True
            certi_all = Certificaciones.objects.filter(idcontrato_id=selected_empleado).values(
                'idcert', 
                'idcontrato__idempleado__papellido',
                'idcontrato__idempleado__pnombre',
                'idcontrato__idempleado__snombre',
                'idcontrato__idempleado__sapellido',
                'destino',
                'fecha',
                'cargo__nombrecargo',
                'salario',
                'tipocontrato',
                'promediovariable',
                'tipocertificacion'
            )
            
            for certi in certi_all:
                nombre_empleado = get_empleado_name(certi)
                salario = "{:,.0f}".format(certi['salario']).replace(',', '.')
                
                certi_data = {
                    'idcert': certi['idcert'],
                    'empleado': nombre_empleado,
                    'destino': certi['destino'],
                    'Salario': salario,
                    'fecha': certi['fecha'],
                    'cargo': certi['cargo__nombrecargo'],
                    'tipo': certi['tipocontrato'],
                    'promedio': certi['promediovariable'],
                    'tipocerti': certi['tipocertificacion'],
                }

                lista_certificaciones.append(certi_data)
    
    
    
    return render(request, 'employees/certificaciones_laborales.html', {
        'contratos': contratos,
        'certificaciones': lista_certificaciones,
        'select': select,
        'select_data': select_data ,
        'selected_empleado':selected_empleado,
        'cont':cont
        
    })




@login_required
@role_required('employee')
def generateworkcertificate(request):
    """
    Genera un certificado laboral en formato PDF según los datos enviados por el usuario.

    Esta vista recibe los datos del formulario POST y genera un PDF con el contenido de un certificado laboral. 
    Usa una plantilla HTML y convierte el contenido a PDF con `xhtml2pdf`.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP del navegador. Se espera que contenga los campos 'empleado', 'contrato', 
        'data_input' y 'data_model' en el método POST.

    Returns
    -------
    HttpResponse
        PDF renderizado con el certificado, enviado en línea al navegador.

    See Also
    --------
    workcertificategenerator : Función que genera el contexto necesario para el certificado.

    Notes
    -----
    - Solo accesible para usuarios con rol `employee`.
    - El contenido se genera con base en una plantilla HTML ('workcertificatework.html').
    - Se usa `xhtml2pdf` (pisa) para convertir HTML a PDF.
    - En caso de error, se muestra un mensaje de error y se redirige a la vista de certificaciones.
    """

    try:
        if request.method == 'POST':
            empleado_id = request.POST.get('empleado')
            contrato_id = request.POST.get('contrato')
            data_input = request.POST.get('data_input')
            data_model = request.POST.get('data_model')
            
            context = workcertificategenerator( contrato_id , data_input ,data_model)
            
            
            
            html_string = render(request, './html/workcertificatework.html', context).content.decode('utf-8')
            
            pdf = BytesIO()
            pisa_status = pisa.CreatePDF(html_string, dest=pdf)
            pdf.seek(0)

            if pisa_status.err:
                return HttpResponse('Error al generar el PDF', status=400)

            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="Certificado.pdf"'
            
            return response
    
    except Exception as e:
        messages.error(request, 'Ocurrio un error inesperado')
        print(e)
        return redirect('employees:certificaciones')


def draw_paragraph(p, text, style, x, y, width):
    paragraph = Paragraph(text, style)
    paragraph.wrapOn(p, width, 200)
    paragraph.drawOn(p, x, y)




@login_required
@role_required('employee')
def certificatedownload(request, idcert):
    try:
        context = workcertificatedownload(idcert)
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Encabezado
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
            p.drawImage(logo, 35, height - 55, width=150, height=50, preserveAspectRatio=True, mask='auto')
        except:
            pass

        # Título
        p.setFont("Helvetica-Bold", 15)
        p.drawCentredString(width / 2, height - 90, "Certificación Laboral")

        # Info de certificado
        p.setFont("Helvetica", 10)
        p.drawCentredString(width - 95, height - 140, f"Certificado #: {context['idcert']} - {context['idempresa']}")
        p.drawCentredString(width - 90, height - 150, f"Código de validación: {context['codigo_confirmacion']}")

        # Estilo párrafos
        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontSize = 10
        style.leading = 14

        # Cuerpo de la certificación
        texts = [
            f"""<para>Certificamos que, <strong>{context["nombre"]}</strong>, identificado(a) con documento de identidad No. {context["identificacion"]}, trabaja en {context["empresa"]}, desde el {context["fecha"]}, desempeñando el cargo de <strong>{context["cargo"]}</strong></para>""",
            f"""<para>Tiene un sueldo básico mensual de <strong>${context["sueldo"]}</strong> y el tipo de contrato laboral es: <strong>{context["tipoc"]}</strong></para>""",
            f"""<para>La presente certificación se expide con destino a : {context["destino"]}</para>""",
            f"""<para>Puede verificar la validez de esta certificación en el email {context["emailrrhh"]}, en los teléfonos que aparecen al pie de este certificado o en este <a href="https://empresas.nomiweb.co/validacion" color="blue"><u>aquí</u></a> usando los códigos de esta certificación.</para>""",
            f"""<para>Fecha de expedición de esta certificación: {context["fecha_certificacion"]}</para>"""
        ]

        y_positions = [height - 200, height - 240, height - 270, height - 310, height - 350]
        for text, y in zip(texts, y_positions):
            draw_paragraph(p, text, style, 35, y, width - 65)

        # Firma
        try:
            firma = ImageReader(f"static/img/{context['firma']}")
            p.drawImage(firma, 35, height - 500, width=150, height=50, preserveAspectRatio=True, mask='auto')
        except:
            pass

        p.setFont("Helvetica", 7)
        p.drawString(35, height - 515, f"{context['rrhh']} - {context['cargo_certificaciones']}")

    
    
        p.setFont("Helvetica", 8)
        p.setFillColor(colors.grey)
        p.drawCentredString(width / 2, 35, f"N.I.T. {context['nit']} - Dirección: Cra.  {context['direccion']} , {context['ciudad']}  - Teléfono: {context['telefono']} - email: {context['emailrrhh']}")


        # Footer
        p.setFont("Helvetica", 8)
        p.setFillColor(colors.grey)
        p.drawCentredString(width / 2, 15, "Outsourcing de Nómina ::: www.nomiweb.co ::: Summa BPO SAS")

        # Metadata y finalizar PDF
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        nombre_archivo = f'Certificado_{context["identificacion"]}_{fecha_actual}.pdf'

        p.setTitle(nombre_archivo)
        p.setAuthor("Nomiweb")
        p.setSubject(f"Comprobante de Nómina {context['identificacion']}")
        p.setCreator("Sistema Nomiweb")
        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
        response.write(pdf)
        return response

    except Exception as e:
        print(e)
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.showPage()
        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        return HttpResponse(pdf, content_type='application/pdf')
    


#def render_certificate(context):
    
    
