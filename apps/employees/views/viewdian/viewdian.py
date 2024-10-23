from django.shortcuts import render,redirect
from apps.common.models import Ingresosyretenciones 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .imggenerate import imggenerate1
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image



from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('employee')
def viewdian(request):
    usuario = request.session.get('usuario', {})
    ide = usuario['idempleado']
    
    # Realizar una única consulta y usar el resultado para ambas necesidades
    reten = Ingresosyretenciones.objects.filter(idempleado=ide)
    years_query = reten.values('anoacumular').first()
    
    years = years_query['anoacumular'] if years_query else None
    
    return render(request, 'employees/viewdian.html', {
        'reten': reten,
        'years': years,
    })


@login_required
@role_required('employee')
def viewdian_empleado(request,idingret ):
    # Generar la imagen usando la función personalizada
    
    certificado = Ingresosyretenciones.objects.filter(idingret=idingret).values('anoacumular').first()
    
    image = imggenerate1(request,idingret)
    
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