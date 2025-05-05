from django.shortcuts import render 
from apps.common.models import Ingresosyretenciones  , Contratosemp 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .imggenerate import imggenerate1
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
from .diangenerate import last_business_day_of_march 



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
    
    
    image = imggenerate1(idingret ,idempresa )
    certificado = Ingresosyretenciones.objects.filter(idingret=idingret).first()
    year, month, day = last_business_day_of_march(certificado.anoacumular.ano)
    # Guardar la imagen en un archivo temporal
    temp_image_path = "temp_image.png"
    image.save(temp_image_path, format='PNG')
    
    response = HttpResponse(content_type='application/pdf')
    file_name = f"Certificado_220_{certificado.idempleado.docidentidad}_{month}_{year}.pdf"
    
    response['Content-Disposition'] = f'inline; filename="{file_name}"'  # Cambiar a 'inline' para abrir en el navegador
    
    pdf = canvas.Canvas(response, pagesize=letter)
    
    # Obtener el tamaño de la página
    page_width, page_height = letter
    
    # Redimensionar la imagen para que ocupe toda la página
    pil_image = Image.open(temp_image_path)
    img_width, img_height = pil_image.size
    aspect_ratio = img_width / img_height

    # Calcular las dimensiones de la imagen para ajustarse a la página manteniendo la relación de aspecto
    if aspect_ratio > (page_width / page_height):
        # La imagen es más ancha en comparación con la página
        new_width = page_width
        new_height = page_width / aspect_ratio
    else:
        # La imagen es más alta en comparación con la página
        new_height = page_height
        new_width = page_height * aspect_ratio

    # Calcular la posición para centrar la imagen
    x_position = (page_width - new_width) / 2
    y_position = (page_height - new_height) / 2
    
    pdf.drawImage(temp_image_path, x_position, y_position, width=new_width, height=new_height)
    
    pdf.showPage()
    pdf.save()
    
    return response





