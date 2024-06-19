from apps.components.datacompanies import datos_cliente
from django.conf import settings
from .diangenerate import last_business_day_of_march 
from apps.employees.models import Ingresosyretenciones 
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from io import BytesIO


def imggenerate1(idingret):
    
    certificado = Ingresosyretenciones.objects.filter(idingret=idingret).first()
    dataempresa = datos_cliente()
    year, month, day = last_business_day_of_march(certificado.anoacumular)
    
    posision1 = {
        'año': {'x': 507, 'y': 68, 'data': str(certificado.anoacumular)},
        'nformulario': {'x': 522, 'y': 115, 'data': str(certificado.idingret)},
        'nit': {'x': 63, 'y': 156, 'data': str(dataempresa['nit_empresa'])},
        'dv': {'x': 304, 'y': 156, 'data': str(dataempresa['dv'])},
        'razon': {'x': 136, 'y': 175, 'data': str(dataempresa['nombre_empresa'])},
        'tipodni': {'x': 64, 'y': 214, 'data':   str(certificado.tipodocumento)},
        'dni': {'x': 134, 'y': 214, 'data': "{:,}".format(int(certificado.docidentidad)).replace(",", ".")},
        'papellido': {'x': 375, 'y': 214, 'data': str(certificado.papellido)},
        'sapellido': {'x': 523, 'y': 214, 'data': str(certificado.sapellido)},
        'pnombre': {'x': 669, 'y': 214, 'data': str(certificado.pnombre)},
        'snombre': {'x': 811, 'y': 214, 'data': str(certificado.snombre)},
        'periodo-1': {'x': 95, 'y': 256, 'data': str(certificado.anoacumular)},
        'periodo-2': {'x': 147, 'y': 256, 'data': '01'},
        'periodo-3': {'x': 184, 'y': 256, 'data': '01'},
        'periodo-4': {'x': 272, 'y': 256, 'data': str(certificado.anoacumular)},
        'periodo-5': {'x': 326, 'y': 256, 'data': '12'},
        'periodo-6': {'x': 360, 'y': 256, 'data': '31'},
        'fechaexp-1': {'x': 401, 'y': 256, 'data': str(year)},
        'fechaexp-2': {'x': 467, 'y': 256, 'data': str(month)},
        'fechaexp-3': {'x': 508, 'y': 256, 'data': str(day)},
        'lugar': {'x': 552, 'y': 256, 'data': str(dataempresa['ciudad_empresa'])},
        'codedespartamento': {'x': 841, 'y': 256, 'data': str(dataempresa['coddpto'])},
        'codemunicipio': {'x': 886, 'y': 256, 'data': str(dataempresa['codciudad'])},
        'retenedor': {'x': 246, 'y': 795, 'data': str(dataempresa['nombre_empresa'])},
    }
    
    value1 = {
        '36': {'data': str(certificado.salarios)},
        '37': {'data': '0'},
        '38': {'data': '0'},
        '39': {'data': str(certificado.honorarios) if certificado.honorarios is not None else '0'},
        '40': {'data': str(certificado.servicios) if certificado.servicios is not None else '0'},
        '41': {'data': str(certificado.comisiones) if certificado.comisiones is not None else '0'},
        '42': {'data': str(certificado.prestacionessociales) if certificado.prestacionessociales is not None else '0'},
        '43': {'data': str(certificado.viaticos) if certificado.viaticos is not None else '0'},
        '44': {'data': str(certificado.gastosderepresentacion) if certificado.gastosderepresentacion is not None else '0'},
        '45': {'data': str(certificado.compensacioncta) if certificado.compensacioncta is not None else '0'},
        '46': {'data': str(certificado.otrospagos) if certificado.otrospagos is not None else '0'},
        '47': {'data': str(certificado.cesantiasintereses) if certificado.cesantiasintereses is not None else '0'},
        '48': {'data': '0'},
        '49': {'data': str(certificado.fondocesantias) if certificado.fondocesantias is not None else '0'},
        '50': {'data': str(certificado.pensiones) if certificado.pensiones is not None else '0'},
        '51': {'data': str(certificado.apoyoeconomico) if certificado.apoyoeconomico is not None else '0'},
        '52': {'data': str(certificado.totalingresosbrutos) if certificado.totalingresosbrutos is not None else '0'},
    }
    
    value2 = {
        '53': {'data': str(certificado.aportessalud) if certificado.aportessalud is not None else '0'},
        '54': {'data': str(certificado.aportespension) if certificado.aportespension is not None else '0'},
        '55': {'data': str(certificado.aportesvoluntarios) if certificado.aportesvoluntarios is not None else '0'},
        '56': {'data': str(certificado.aportesvoluntarios) if certificado.aportesvoluntarios is not None else '0'},
        '57': {'data': str(certificado.aportesafc) if certificado.aportesafc is not None else '0'},
        '58': {'data': str(certificado.aportesavc) if certificado.aportesavc is not None else '0'},
        '59': {'data': str(certificado.ingresolaboralpromedio) if certificado.ingresolaboralpromedio is not None else '0'},
        '60': {'data': str(certificado.retefuente) if certificado.retefuente is not None else '0'},
    }

    # value1
    value1 = {k: {'data': '{:,.0f}'.format(float(v['data']))} if v['data'].replace('.', '', 1).isdigit() else v for k, v in value1.items()}

    # value2
    value2 = {k: {'data': '{:,.0f}'.format(float(v['data']))} if v['data'].replace('.', '', 1).isdigit() else v for k, v in value2.items()}


    image = Image.open(settings.STATICFILES_DIRS[0] + "/img/dian/220-2023.jpg")
    draw = ImageDraw.Draw(image)
    font_path = settings.STATICFILES_DIRS[0] + '/fonts/SpecialElite-Regular.ttf'
    font = ImageFont.truetype('cour.ttf', size=18)
    fill_color = "black"

    for campo, info in posision1.items():
        text = str(info['data'])
        position = (info['x'], info['y'])
        draw.text(position, text, font=font, fill=fill_color)

    max_width, max_height = image.size
    x = max_width - 50
    y = 294
    line_spacing = 7

    for campo, info in value1.items():
        dta = info['data']
        bbox = draw.textbbox((0, 0), dta, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        start_x = x - text_width
        draw.text((start_x, y), dta, font=font, fill=fill_color)
        y += text_height + line_spacing

    y += 20
    line_spacing = 8
    for campo, info in value2.items():
        dta = info['data']
        bbox = draw.textbbox((0, 0), dta, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        start_x = x - text_width
        draw.text((start_x, y), dta, font=font, fill=fill_color)
        y += text_height + line_spacing
    
    return image