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

@login_required
@role_required('company','accountant')
def settlementlistdownload(request,idliqui):
    """
    Vista para generar y descargar en PDF la liquidación detallada de un contrato.

    Esta vista genera un archivo PDF con la información de liquidación de un contrato específico, utilizando una plantilla HTML 
    y la función `settlementgenerator`. El archivo generado se muestra en el navegador o se descarga directamente.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene la sesión del usuario autenticado y sus datos de empresa.
    idliqui : int
        Identificador único de la liquidación que se desea descargar en formato PDF.

    Returns
    -------
    HttpResponse
        Devuelve una respuesta con el archivo PDF generado, con el tipo de contenido 'application/pdf'.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol 'company' o 'accountant' para acceder a esta vista.
    Se utiliza `xhtml2pdf` para convertir el HTML a PDF.
    En caso de error durante la generación del PDF, se devuelve un mensaje de error con estado HTTP 400.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    context = settlementgenerator(idliqui,idempresa)

    html_string = render(request, './html/liquidacion.html', context).content.decode('utf-8')
    
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=pdf)
    pdf.seek(0)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=400)
    
    nombre_archivo = f'Certificado_{context["cc"]}_{fecha_actual}.pdf'

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
    
    return response