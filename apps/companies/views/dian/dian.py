from django.shortcuts import render 
from apps.common.models import Ingresosyretenciones  , Contratosemp 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .imggenerate import imggenerate1 , pdfgenerate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
from .diangenerate import last_business_day_of_march 
from PyPDF2 import PdfMerger
import tempfile
from django.http import FileResponse


def viewdian(request):
    """
    Muestra los ingresos y retenciones de un empleado basado en su estado de contrato.

    Esta vista permite al usuario ver los ingresos y retenciones de un empleado específico. 
    Se filtran los empleados según su estado de contrato (activo o inactivo), y si se selecciona 
    un empleado, se muestra la información correspondiente a ese empleado.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los parámetros 'empleado' y 'data'.
        - 'empleado' es el identificador del empleado seleccionado (opcional).
        - 'data' indica el estado de contrato del empleado: 'activo' o 'inactivo'.

    Returns
    -------
    HttpResponse
        Devuelve una página HTML con la lista de empleados y la información de ingresos y retenciones 
        para el empleado seleccionado (si corresponde).

    See Also
    --------
    Contratosemp : Modelo que representa los empleados con su estado de contrato.
    Ingresosyretenciones : Modelo que representa los ingresos y retenciones de los empleados.
    
    Notes
    -----
    El usuario debe estar autenticado para acceder a esta vista.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    selected_empleado = request.GET.get('empleado')
    selected_contra = request.GET.get('data')

    # Valor por defecto para empleados_select
    empleados_select = []

    if selected_contra == "activo":
        empleados_select = Contratosemp.objects.filter(estadocontrato=1 , id_empresa_id = idempresa ).order_by('papellido').values(
            'pnombre', 'snombre', 'papellido', 'sapellido', 'idempleado'
        )
    elif selected_contra == "inactivo":
        empleados_select = Contratosemp.objects.filter(estadocontrato=2, id_empresa_id = idempresa  ).order_by('papellido').values(
            'pnombre', 'snombre', 'papellido', 'sapellido', 'idempleado'
        )

    if selected_empleado:
        # Filtrar los ingresos y retenciones del empleado seleccionado
        reten = Ingresosyretenciones.objects.filter(idempleado=selected_empleado)
        # Si existen registros, obtener el primer año acumulado, de lo contrario, dejar la variable vacía
        years_query = reten.values('anoacumular').first() if reten.exists() else None
    else:
        reten = []
        years_query = {}

    context = {
        'empleados_select': empleados_select,
        'selected_empleado': selected_empleado,
        'selected_contra': selected_contra,
        'reten': reten,
        'years_query': years_query,
    }

    return render(request, './companies/viewdian.html', context)



def viewdian_download(request,idingret ):
    
    """
    Genera y descarga un certificado en formato PDF con una imagen del certificado de ingresos y retenciones.

    Esta vista genera un certificado en formato PDF para el ingreso y retención de un empleado, 
    incluyendo una imagen generada previamente. El certificado se descarga como un archivo PDF.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene el identificador del registro de ingresos y retenciones.
        - 'idingret' es el identificador del registro de ingresos y retenciones.

    Returns
    -------
    HttpResponse
        Devuelve un archivo PDF que contiene el certificado generado.

    See Also
    --------
    imggenerate1 : Función personalizada para generar la imagen del certificado.
    last_business_day_of_march : Función personalizada que calcula el último día hábil de marzo.
    Ingresosyretenciones : Modelo que representa los ingresos y retenciones de los empleados.

    Notes
    -----
    El usuario debe estar autenticado para acceder a esta vista.
    """

    # Generar la imagen usando la función personalizada
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    pdf_buffer = pdfgenerate(idingret, idempresa)

    certificado = Ingresosyretenciones.objects.filter(idingret=idingret).first()
    year, month, day = last_business_day_of_march(certificado.anoacumular.ano)

    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')

    file_name = f"Certificado_220_{certificado.idempleado.docidentidad}_{year}.pdf"
    response['Content-Disposition'] = f'inline; filename="{file_name}"'

    return response



@login_required
def viewdian_download_massive(request):
    """
    Genera un PDF masivo de certificados y lo visualiza inline sin cargar todo en memoria.
    """
    if request.method == 'POST':

        usuario = request.session.get('usuario', {})
        idempresa = usuario['idempresa']
        year = request.POST.get('year')
        

        certificados = Ingresosyretenciones.objects.filter(
            anoacumular__ano=year, 
            id_empresa_id=idempresa
        )

        # Archivo temporal en disco (no se borra auto para FileResponse)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_path = temp_file.name
        temp_file.close()  # Cerramos para escribir

        merger = PdfMerger()

        for cert in certificados:  # No carga en memoria
            try:
                pdf_buffer = pdfgenerate(cert.idingret, idempresa)
                merger.append(pdf_buffer)
            except Exception as e:
                print(f"Error con certificado {cert.idingret}: {e}")
                continue

        merger.write(temp_path)
        merger.close()

        # Abre y envía como inline
        with open(temp_path, 'rb') as f:
            pdf_content = f.read()

        # Limpia temporal
        import os
        os.unlink(temp_path)

        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="Certificados_Masivos_{year}.pdf"'

        return response



