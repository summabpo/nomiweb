from apps.components.datacompanies import datos_cliente
from django.conf import settings
from .diangenerate import last_business_day_of_march 
from apps.employees.models import Ingresosyretenciones 
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from io import BytesIO
from apps.components.humani import format_value



def imggenerate1(idingret):
    
    certificado = Ingresosyretenciones.objects.filter(idingret=idingret).first()
    dataempresa = datos_cliente()
    year, month, day = last_business_day_of_march(certificado.anoacumular)
    
    posision1 = {
        'año': {'x': 507, 'y': 68, 'data': str(certificado.anoacumular)},
        'nformulario': {'x': 522, 'y': 115, 'data': str(certificado.idingret)},
        'nit': {'x': 63, 'y': 156, 'data': str(dataempresa['nit'])},
        'dv': {'x': 304, 'y': 156, 'data': str(dataempresa['dv'])},
        'razon': {'x': 136, 'y': 175, 'data': str(dataempresa['nombreempresa'])},
        'tipodni': {'x': 64, 'y': 214, 'data':   str(certificado.tipodocumento)},
        'dni': {'x': 134, 'y': 214, 'data': "{:,}".format(int(certificado.docidentidad)).replace(",", ".")},
        'papellido': {'x': 375, 'y': 214, 'data': str(certificado.papellido)},
        'sapellido': {'x': 523, 'y': 214, 'data': str(certificado.sapellido)},
        'pnombre': {'x': 669, 'y': 214, 'data': str(certificado.pnombre)},
        'snombre': {'x': 811, 'y': 214, 'data': str(certificado.snombre)},
        'periodo-1': {'x': 95, 'y': 254, 'data': str(certificado.anoacumular)},
        'periodo-2': {'x': 147, 'y': 254, 'data': '01'},
        'periodo-3': {'x': 184, 'y': 254, 'data': '01'},
        'periodo-4': {'x': 272, 'y': 254, 'data': str(certificado.anoacumular)},
        'periodo-5': {'x': 326, 'y': 254, 'data': '12'},
        'periodo-6': {'x': 360, 'y': 254, 'data': '31'},
        'fechaexp-1': {'x': 401, 'y': 254, 'data': str(year)},
        'fechaexp-2': {'x': 467, 'y': 254, 'data': str(month)},
        'fechaexp-3': {'x': 508, 'y': 254, 'data': str(day)},
        'lugar': {'x': 552, 'y': 254, 'data': str(dataempresa['ciudad'])},
        'codedespartamento': {'x': 841, 'y': 254, 'data': str(dataempresa['coddpto'])},
        'codemunicipio': {'x': 886, 'y': 254, 'data': str(dataempresa['codciudad'])},
        'retenedor': {'x': 246, 'y': 795, 'data': str(dataempresa['nombreempresa'])},
    }
    
    value1 = {
        '36': {'data': format_value(certificado.salarios)},  
        '37': {'data': '0'},
        '38': {'data': '0'},
        '39': {'data': format_value(certificado.honorarios)}, 
        '40': {'data': format_value(certificado.servicios)},
        '41': {'data': format_value(certificado.comisiones)},
        '42': {'data': format_value(certificado.prestacionessociales)},
        '43': {'data': format_value(certificado.viaticos)},
        '44': {'data': format_value(certificado.gastosderepresentacion)},
        '45': {'data': format_value(certificado.compensacioncta)},
        '46': {'data': format_value(certificado.otrospagos)},
        '47': {'data': format_value(certificado.cesantiasintereses)},
        '48': {'data': '0'},
        '49': {'data': format_value(certificado.fondocesantias)},
        '50': {'data': format_value(certificado.pensiones)},
        '51': {'data': format_value(certificado.apoyoeconomico)},
        '52': {'data': format_value(certificado.totalingresosbrutos)},
    }
    
    value2 = {
        '53': {'data': format_value (certificado.aportessalud)},
        '54': {'data': format_value (certificado.aportespension)},
        '55': {'data': format_value (certificado.aportesvoluntarios)},
        '56': {'data': format_value (certificado.aportesvoluntarios)},
        '57': {'data': format_value (certificado.aportesafc)},
        '58': {'data': format_value (certificado.aportesavc)},
        '59': {'data': format_value (certificado.ingresolaboralpromedio)},
        '60': {'data': format_value (certificado.retefuente)},
    }

    # value1
    value1 = {k: {'data': '{:,.0f}'.format(float(v['data']))} if v['data'].replace(',', '.', 1).isdigit() else v for k, v in value1.items()}

    # value2
    value2 = {k: {'data': '{:,.0f}'.format(float(v['data']))} if v['data'].replace(',', '.', 1).isdigit() else v for k, v in value2.items()}


    image = Image.open(settings.STATICFILES_DIRS[0] + "/img/dian/220-2023.jpg")
    draw = ImageDraw.Draw(image)
    font_path = settings.STATICFILES_DIRS[0] + '/fonts/cour.ttf'
    font = ImageFont.truetype(font_path, size=18)
    fill_color = "black"

    for campo, info in posision1.items():
        text = str(info['data'])
        position = (info['x'], info['y'])
        draw.text(position, text, font=font, fill=fill_color)

    max_width, max_height = image.size
    x = max_width - 50
    y = 294
    line_spacing = 8

    for campo, info in value1.items():
        dta = info['data']
        bbox = draw.textbbox((0, 0), dta, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        start_x = x - text_width
        draw.text((start_x, y), dta, font=font, fill=fill_color)
        y += text_height + line_spacing

    y = 640
    line_spacing = 9
    
    for campo, info in value2.items():
        dta = info['data']
        bbox = draw.textbbox((0, 0), dta, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        start_x = x - text_width
        draw.text((start_x, y), dta, font=font, fill=fill_color)
        y += text_height + line_spacing 
    
    return image