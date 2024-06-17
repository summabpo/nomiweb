from django.shortcuts import render,redirect
from apps.employees.models import Ingresosyretenciones 
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse
from apps.components.datacompanies import datos_cliente



def viewdian(request):
    ide = request.session.get('idempleado', {})
    
    # Realizar una única consulta y usar el resultado para ambas necesidades
    reten = Ingresosyretenciones.objects.filter(idempleado=ide)
    years_query = reten.values('anoacumular').first()
    
    years = years_query['anoacumular'] if years_query else None
    
    return render(request, 'employees/viewdian.html', {
        'reten': reten,
        'years': years,
    })


def viewdian_empleado(request,idingret ):
    
    
    
    ide = request.session.get('idempleado', {})
    certificado = Ingresosyretenciones.objects.filter(idingret=idingret).first()
    dataempresa = datos_cliente()
    
    posision1 = {
        'año' : { 
            'x':507,
            'y':68,
            'data': str(certificado.anoacumular)
        },
        'nformulario':{
            'x':522, 
            'y':115,
            'data': str(certificado.idingret)
        },
        'nit':{
            'x':63,
            'y':152,
            'data': str(dataempresa['nit_empresa'])
        },
        'dv':{
            'x':304,
            'y':154,
            'data': str(dataempresa['dv']) # str(certificado.docidentidad) 304, 154
        },
        'razon':{
            'x':136, 
            'y':175,
            'data': str(certificado.docidentidad)
        },
        'tipodni':{
            'x':64, 
            'y':212,
            'data': str(certificado.tipodocumento)
        },
        'dni':{
            'x':134, 
            'y':210,
            'data': str(certificado.docidentidad)
        },
        'papellido':{
            'x':375, 
            'y':209,
            'data': str(certificado.papellido)
        },
        'sapellido':{
            'x':523,
            'y':213, 
            'data': str(certificado.sapellido)
        },
        'pnombre':{
            'x':669, 
            'y':214,
            'data': str(certificado.pnombre)
        },
        'snombre':{
            'x':811, 
            'y':214,
            'data': str(certificado.snombre)
        },
        ## periodo fijo y automatico 
        'periodo-1':{
            'x':95, 
            'y':252,
            'data': str(certificado.anoacumular)
        },
        'periodo-2':{
            'x':147, 
            'y':252,
            'data': '01'
        },
        'periodo-3':{
            'x':184,
            'y':252,
            'data': '01'
        },
        'periodo-4':{
            'x':272,
            'y':252,
            'data': str(certificado.anoacumular)
        },
        'periodo-5':{
            'x':326,
            'y':252,
            'data': '12'
        },
        'periodo-6':{
            'x':360,
            'y':252,
            'data': '31'
        },
        'fechaexp':{
            'x':0,
            'y':0,
            'data': str(certificado.docidentidad)
        },
        'lugar':{
            'x':552, 
            'y':249,
            'data': str(dataempresa['ciudad_empresa'])
        },
        'codedespartamento':{
            'x':841, 
            'y':252,
            'data': str(dataempresa['coddpto'])
        },
        'codemunicipio':{
            'x':886, 
            'y':252,
            'data': str(dataempresa['codciudad'])
        },
        
    }
    
    
    
    
    image = Image.open("static/img/dian/220-2023.jpg")
    draw = ImageDraw.Draw(image)
    
    font = ImageFont.truetype("arial.ttf", size=18)
    # Color del texto
    fill_color = "black"
    # Agregar texto a la imagen
    
    
    for campo, info in posision1.items():    
        text = str(info['data'])
        position = (info['x'], info['y'])  # Coordenadas (x, y) del texto
        draw.text(position, text, font=font, fill=fill_color)

    # Guardar la imagen con el texto agregado
    image.save("imagen_con_texto.jpg")
    
    response = HttpResponse(content_type='image/jpeg')
    image.save(response, 'JPEG')
    return response





