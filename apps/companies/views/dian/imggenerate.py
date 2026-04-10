from apps.components.datacompanies import datos_cliente
from django.conf import settings
from .diangenerate import last_business_day_of_march 
from apps.common.models import Ingresosyretenciones 
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from apps.components.humani import format_value

import json
from io import BytesIO
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

from apps.components.datacompanies import datos_cliente
from django.conf import settings
from .diangenerate import last_business_day_of_march 
from apps.common.models import Ingresosyretenciones 
from apps.components.humani import format_value


def imggenerate1(idingret , idempresa):
    
    certificado = Ingresosyretenciones.objects.filter(idingret=idingret).first()
    dataempresa = datos_cliente(idempresa)
    year, month, day = last_business_day_of_march(certificado.anoacumular.ano)
    
    posision1 = {
        'año': {'x': 507, 'y': 68, 'data': str(certificado.anoacumular.ano)},
        'nformulario': {'x': 522, 'y': 115, 'data': str(certificado.idingret)},
        'nit': {'x': 63, 'y': 156, 'data': str(dataempresa['nit'])},
        'dv': {'x': 304, 'y': 156, 'data': str(dataempresa['dv'])},
        'razon': {'x': 136, 'y': 175, 'data': str(dataempresa['nombreempresa'])},
        'tipodni': {'x': 64, 'y': 214, 'data':   str(certificado.idempleado.tipodocident.codigo)},
        'dni': {'x': 134, 'y': 214, 'data': "{:,}".format(int(certificado.idempleado.docidentidad)).replace(",", ".")},
        'papellido': {'x': 375, 'y': 214, 'data': str(certificado.idempleado.papellido)},
        'sapellido': {'x': 523, 'y': 214, 'data': str(certificado.idempleado.sapellido)},
        'pnombre': {'x': 669, 'y': 214, 'data': str(certificado.idempleado.pnombre)},
        'snombre': {'x': 811, 'y': 214, 'data': str(certificado.idempleado.snombre)},
        'periodo-1': {'x': 95, 'y': 254, 'data': str(certificado.anoacumular.ano)},
        'periodo-2': {'x': 147, 'y': 254, 'data': '01'},
        'periodo-3': {'x': 184, 'y': 254, 'data': '01'},
        'periodo-4': {'x': 272, 'y': 254, 'data': str(certificado.anoacumular.ano)},
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



# =========================
# Pdf Dian 2.0
# =========================
def pdfgenerate(idingret, idempresa):
    
    certificado = Ingresosyretenciones.objects.filter(idingret=idingret).first()
    dataempresa = datos_cliente(idempresa)
    year, month, day = last_business_day_of_march(certificado.anoacumular.ano)

    # =========================
    # CARGAR JSON
    # =========================
    with open("apps/companies/views/dian/formatos_220.json", encoding="utf-8") as f:
        formatos = json.load(f)

    config = formatos[str(certificado.anoacumular.ano)]
    coords = config["fields"]
    pdf_base_path = settings.STATICFILES_DIRS[0] + "/pdf/" + config["pdf"]

    # =========================
    # DATOS DINÁMICOS
    # =========================
    datos = {
        "anio": certificado.anoacumular.ano,
        "nformulario": str(certificado.idingret),

        "empresa": {
            "nit": str(dataempresa['nit']),
            "dv": str(dataempresa['dv']),
            "razon": str(dataempresa['nombreempresa'])
        },

        "pagado": {
            "razon": str(dataempresa['nombreempresa'])
        },

        "empleado": {
            "tipodni": str(certificado.idempleado.tipodocident.codigo),
            "dni": "{:,}".format(int(certificado.idempleado.docidentidad)).replace(",", "."),
            "papellido": str(certificado.idempleado.papellido),
            "sapellido": str(certificado.idempleado.sapellido),
            "pnombre": str(certificado.idempleado.pnombre),
            "snombre": str(certificado.idempleado.snombre),
        },




        "periodo": {
            "inicio": [certificado.anoacumular.ano, "01", "01"],
            "fin": [certificado.anoacumular.ano, "12", "31"]
        },

        "fecha_expedicion": [year, month, day],

        "ubicacion": {
            "lugar": str(dataempresa['ciudad']),
            "departamento": str(dataempresa['coddpto']),
            "municipio": str(dataempresa['codciudad'])
        },

        "firma": {
            "retenedor": str(dataempresa['nombreempresa'])
        }
    }

    # =========================
    # VALUE BLOCKS DESDE JSON
    # =========================
    value_blocks = config.get("value_blocks", {})

    value1_block = value_blocks.get("value1", {})
    value2_block = value_blocks.get("value2", {})

    value1 = {
        '36': certificado.salarios,
        '37': 0,
        '38': 0,
        '39': certificado.honorarios,
        '40': certificado.servicios,
        '41': certificado.comisiones,
        '42': certificado.prestacionessociales,
        '43': certificado.viaticos,
        '44': certificado.gastosderepresentacion,
        '45': certificado.compensacioncta,
        '46': certificado.otrospagos,
        '47': certificado.cesantiasintereses,
        '48': 0,
        '49': certificado.fondocesantias,
        '50': certificado.pensiones,
        '51': certificado.apoyoeconomico,
        '52': certificado.totalingresosbrutos,
    }

    value2 = {
        '53': certificado.aportessalud,
        '54': certificado.aportespension,
        '55': certificado.aportesvoluntarios,
        '56': certificado.aportesvoluntarios,
        '57': certificado.aportesafc,
        '58': certificado.aportesavc,
        '59': certificado.ingresolaboralpromedio,
        '60': certificado.retefuente,
    }

    def fmt(v):
        try:
            return "{:,.0f}".format(float(v))
        except:
            return "0"

    # =========================
    # FUNCION GENERICA VALUE BLOCK
    # =========================
    def draw_value_block(block, values_dict):
        x = block["x"]          # punto DERECHO fijo
        y = block["y_start"]
        step = block["step"]

        for key in sorted(values_dict.keys(), key=int):
            value = fmt(values_dict[key])

            c.drawRightString(x, y, value)

            y -= step

    # =========================
    # CREAR OVERLAY
    # =========================
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Courier", 9)

    # =========================
    # CAMPOS JSON
    # =========================
    def draw_fields(data_block, coord_block):
        for key, value in data_block.items():

            if key not in coord_block:
                continue

            if isinstance(value, dict):
                draw_fields(value, coord_block[key])

            elif isinstance(value, list):
                for i, v in enumerate(value):
                    try:
                        pos = coord_block[key][i]
                        c.drawString(pos["x"], pos["y"], str(v))
                    except:
                        continue

            else:
                pos = coord_block[key]
                c.drawString(pos["x"], pos["y"], str(value))

    draw_fields(datos, coords)

    # =========================
    # VALUE BLOCKS (AUTO STEP)
    # =========================
    draw_value_block(value1_block, value1)
    draw_value_block(value2_block, value2)

    c.save()
    buffer.seek(0)

    # =========================
    # MERGE PDF
    # =========================
    base_pdf = PdfReader(pdf_base_path)
    overlay_pdf = PdfReader(buffer)

    writer = PdfWriter()

    for i in range(len(base_pdf.pages)):
        page = base_pdf.pages[i]
        if i < len(overlay_pdf.pages):
            page.merge_page(overlay_pdf.pages[i])
        writer.add_page(page)

    output_buffer = BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer


""" 

"empleado": {
        "tipodni": { "x": 55, "y": 650 },
        "dni": { "x": 85, "y": 650 },
        "papellido": { "x": 230, "y": 687 },
        "sapellido": { "x":310, "y": 687 },
        "pnombre": { "x": 400, "y": 687 },
        "snombre": { "x": 500, "y": 687 }
      },

"""
