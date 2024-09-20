from django.shortcuts import render 
from apps.employees.models import Ingresosyretenciones 
from apps.companies.models import Contratosemp 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .imggenerate import imggenerate1
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image




def viewdian(request):
    selected_empleado = request.GET.get('empleado')
    selected_contra = request.GET.get('data')

    # Valor por defecto para empleados_select
    empleados_select = []

    if selected_contra == "activo":
        empleados_select = Contratosemp.objects.filter(estadocontrato=1).order_by('papellido').values(
            'pnombre', 'snombre', 'papellido', 'sapellido', 'idempleado'
        )
    elif selected_contra == "inactivo":
        empleados_select = Contratosemp.objects.filter(estadocontrato=2).order_by('papellido').values(
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
    # Generar la imagen usando la función personalizada
    
    image = imggenerate1(idingret)
    
    # Guardar la imagen en un archivo temporal
    temp_image_path = "temp_image.png"
    image.save(temp_image_path, format='PNG')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="imagen_modificada.pdf"'  # Cambiar a 'inline' para abrir en el navegador
    
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





