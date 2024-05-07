from django.http import HttpResponse
from django.template.loader import render_to_string
import os
from django.conf import settings
from django.utils.encoding import smart_str
from io import BytesIO
from xhtml2pdf import pisa



from django.shortcuts import render



def startemployees(request):
    
    datos = {
        'nombre_cliente': 'Juan Pérez',
        'monto': 100,
        'fecha': '2024-05-07',
    }
    
    return render(request, './html/comprobante_nomina.html' , {'datos': datos})




def descargar_recibo(request):
    # Genera el contenido del recibo usando una plantilla
    datos = {
        'nombre_cliente': 'Juan Pérez',
        'monto': 100,
        'fecha': '2024-05-07',
    }
    contenido_html = render_to_string('html/comprobante_nomina.html', {'datos': datos})

    # Genera el archivo PDF a partir del contenido HTML
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(contenido_html, dest=buffer)
    
    # Verifica si la conversión fue exitosa
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    # Prepara la respuesta de descarga
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="recibo.pdf"'

    # Copia el contenido del buffer al response y cierra el buffer
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response