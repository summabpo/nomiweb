from django.shortcuts import render
from django.db.models import Sum
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from apps.employees.forms.certificado_laboral import FormularioCertificaciones
from apps.employees.context_global import datos_cliente, datos_empleado
from django.utils import timezone
import pytz
import locale
import random
import string
import datetime

# models
from django.db.models import Q
from apps.employees.models import  Certificaciones, Nomina
locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

idn = 359

def generar_codigo():
    caracteres = string.ascii_letters + string.digits  # Letras mayúsculas, minúsculas y dígitos
    codigo = ''.join(random.choice(caracteres) for _ in range(5))
    return codigo

def calculo_salario_promedio():
    mes_actual = datetime.datetime.now().month
    ano_x = datetime.datetime.now().year

    mes_1 = mes_actual - 1
    ano_1 = ano_x
    if mes_1 == 0:
        mes_1 = 12
        ano_1 -= 1

    mes_2 = mes_actual - 2
    ano_2 = ano_x
    if mes_2 <= 0:
        mes_2 += 12
        ano_2 -= 1

    mes_3 = mes_actual - 3
    ano_3 = ano_x
    if mes_3 <= 0:
      mes_3 += 12
      ano_3 -= 1
    
    meses_dict = {
    1: "ENERO",
    2: "FEBRERO",
    3: "MARZO",
    4: "ABRIL",
    5: "MAYO",
    6: "JUNIO",
    7: "JULIO",
    8: "AGOSTO",
    9: "SEPTIEMBRE",
    10: "OCTUBRE",
    11: "NOVIEMBRE",
    12: "DICIEMBRE"
}
    nombre_mes_1 = meses_dict.get(mes_1, "Mes inválido")
    nombre_mes_2 = meses_dict.get(mes_2, "Mes inválido")
    nombre_mes_3 = meses_dict.get(mes_3, "Mes inválido")

    return nombre_mes_1, nombre_mes_2, nombre_mes_3, ano_1, ano_2, ano_3




def vista_certificaciones(request):
    datose = datos_empleado()
    zona_horaria = pytz.timezone('America/Bogota')
    #CALCULA SALARIO PROMEDIO ULTIMOS 3 MESES
    nombre_mes_1, nombre_mes_2, nombre_mes_3, ano_1, ano_2, ano_3 = calculo_salario_promedio()

    idc = datose['idc']
    if request.method == 'POST':
        formulario = FormularioCertificaciones(request.POST)

        if formulario.is_valid():
            fecha_actual = timezone.now().astimezone(zona_horaria)
            destino = formulario.cleaned_data['destino']
            modelo = formulario.cleaned_data['modelo']
            salario = datose['salario']

            queryset = Nomina.objects.filter(
                (Q(idconcepto__baseprestacionsocial = 1)),
                (Q(mesacumular=nombre_mes_1) & Q(anoacumular=ano_1) |
                Q(mesacumular=nombre_mes_2) & Q(anoacumular=ano_2) |
                Q(mesacumular=nombre_mes_3) & Q(anoacumular=ano_3)),
                idcontrato = idc,
                valor__gt=0
                )

            if queryset.exists():
                salario_promedio = (queryset.aggregate(salario_promedio=Sum('valor'))['salario_promedio'])/3
            else:
                salario_promedio = 0

            if modelo=='2':
                salario_certificado=salario_promedio + salario
            else:
                salario_certificado=salario

            codigo_confirmacion = generar_codigo()
            tipo_certificado = modelo
            cargo = datose['cargo']
            ide = datose['ide']
            tipo_contrato = datose['tipo_contrato']
            nombre_contrato = datose['nombre_contrato']
            certificacion = Certificaciones(destino=destino, idcontrato=idc, idempleado=ide, salario=salario_certificado, cargo=cargo, tipocontrato=nombre_contrato, codigoconfirmacion = codigo_confirmacion, promediovariable = tipo_certificado )
            certificacion.save()
            certificacion.fecha = fecha_actual
            certificacion.save()
    else:
        formulario = FormularioCertificaciones()

    lista_certificaciones = Certificaciones.objects.filter(idcontrato=idc).order_by('-idcert')[:10]

    return render(request, 'employees/certificaciones_laborales.html', {
        'formulario': formulario,
        'certificaciones': lista_certificaciones
    })

def genera_certificaciones(request, idcert):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="certificado.pdf"'
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width,height=letter

    #DATOS DE LA EMPRESA
    datosc = datos_cliente()
    nombre_empresa = datosc['nombre_empresa']
    nombre_rrhh = datosc['nombre_rrhh']
    website_empresa = datosc['website_empresa']
    nit_empresa = datosc['nit_empresa']
    direccion_empresa = datosc['direccion_empresa']
    ciudad_empresa = datosc['ciudad_empresa']
    telefono_empresa = datosc['telefono_empresa']
    email_empresa = datosc['email_empresa']
    logo_empresa = datosc['logo_empresa']
    id_cliente = datosc['id_cliente']
    cargo_certificaciones = datosc['cargo_certificaciones']
    firma_certificaciones = datosc['firma_certificaciones']

    #DATOS EMPLEADO
    datose = datos_empleado()
    idc = datose['idc']
    nombre_completo = datose['nombre_completo']
    docidentidad = datose['docidentidad']
    fechainiciocontrato = datose['fechainiciocontrato']
    cargo = datose['cargo']
    nombre_contrato = datose['nombre_contrato']

    #DATOS CERTIFICACION
    salario = Certificaciones.objects.get(idcert=idcert).salario
    salario_formateado = locale.format_string("%0.0f", salario, grouping=True, monetary=True)
    destino = Certificaciones.objects.get(idcert=idcert).destino
    id_cert = Certificaciones.objects.get(idcert=idcert).idcert
    codigo_validacion = Certificaciones.objects.get(idcert=idcert).codigoconfirmacion
    fecha_certificacion = Certificaciones.objects.get(idcert=idcert).fecha
    seleccion_tipo = Certificaciones.objects.get(idcert=idcert).promediovariable

    #TEXTO 1 SALARIO BASICO
    p1=Paragraph(f"""<para align="justify" fontsize="14" leading="18">Certificamos que, <b>{nombre_completo}</b>, identificado(a) con documento de identidad No. {docidentidad}, trabaja en <b>{nombre_empresa}</b>, desde el {fechainiciocontrato}, desempeñando el cargo de <b>{cargo}</b>.<br/><br/>
    Tiene un sueldo básico mensual de <b>${salario_formateado}</b> y el tipo de contrato laboral es: {nombre_contrato}.<br/><br/> 
    La presente certificación se expide con destino a: <b>{destino}</b>.<br/><br/>
    Puede verificar la validez de esta certificación en el email, en los teléfonos que aparecen al pie de este certificado o en este enlace usando los códigos de esta certificación: https://www.empresas.nomiweb.co/validación</para>""")

    #TEXTO 2 SALARIO PROMEDIO
    p2=Paragraph(f"""<para align="justify" fontsize="14" leading="18">Certificamos que, <b>{nombre_completo}</b>, identificado(a) con documento de identidad No. {docidentidad}, trabaja en <b>{nombre_empresa}</b>, desde el {fechainiciocontrato}, desempeñando el cargo de <b>{cargo}</b>.<br/><br/>
    Tiene un salario promedio mensual de <b>${salario_formateado}</b> y el tipo de contrato laboral es: {nombre_contrato}.<br/><br/> 
    La presente certificación se expide con destino a: <b>{destino}</b>.<br/><br/>
    Puede verificar la validez de esta certificación en el email, en los teléfonos que aparecen al pie de este certificado o en este enlace usando los códigos de esta certificación: https://www.empresas.nomiweb.co/validación</para>""")

    #TEXTO 3 SIN SALARIO
    p3=Paragraph(f"""<para align="justify" fontsize="14" leading="18">Certificamos que, <b>{nombre_completo}</b>, identificado(a) con documento de identidad No. {docidentidad}, trabaja en <b>{nombre_empresa}</b>, desde el {fechainiciocontrato}, desempeñando el cargo de <b>{cargo}</b>.<br/><br/>
    El tipo de contrato laboral es: {nombre_contrato}.<br/><br/> 
    La presente certificación se expide con destino a: <b>{destino}</b>.<br/><br/>
    Puede verificar la validez de esta certificación en el email, en los teléfonos que aparecen al pie de este certificado o en este enlace usando los códigos de esta certificación: https://www.empresas.nomiweb.co/validación</para>""")

    if seleccion_tipo == 1:
        p1.wrapOn(p,500,400)
        p1.drawOn(p, 60, 320)
    elif seleccion_tipo == 2:
        p2.wrapOn(p,500,400)
        p2.drawOn(p, 60, 320)
    elif seleccion_tipo == 3:
         p3.wrapOn(p,500,400)
         p3.drawOn(p, 60, 320)



    # VARIABLES PDF
    p.setFont("Helvetica-Bold", 20)
    nom_empresa_width = p.stringWidth(nombre_empresa, "Helvetica", 24)
    nom_empresa_x = (width - nom_empresa_width) / 2
    p.drawString(nom_empresa_x, height-25, nombre_empresa)

    p.setFont("Helvetica-Bold", 15)
    nit_width = p.stringWidth(nit_empresa, "Helvetica-Bold", 15)
    nit_x =  (width - nit_width) / 2
    p.drawString(nit_x, height-55, nit_empresa)

    p.setFont("Helvetica-Bold", 15)
    web_width = p.stringWidth(website_empresa, "Helvetica-Bold", 15)
    web_x =  (width - web_width) / 2
    p.drawString(web_x, height-85, website_empresa)


    logo = ImageReader(f'static/img/{logo_empresa}')
    p.drawImage(logo, 20, 650, width=100, preserveAspectRatio=True, mask='auto')
    p.line(5,700,600,700)
    p.setFont("Helvetica-Bold", 15)
    p.drawString(230,650,'Certificación Laboral')
    p.setFont("Helvetica", 8)
    p.drawString(430,615,f'Certificado # {id_cliente}-{id_cert}')
    p.drawString(430,600, f'Código de Validación: {codigo_validacion}')
    p.setFont("Helvetica", 12)
    p.drawString(60,280, f'Fecha de expedición de esta certificación: {fecha_certificacion}')
    firma = ImageReader(f'static/img/{firma_certificaciones}')
    p.drawImage(firma, 60, 200, width=170, preserveAspectRatio=True, mask='auto')
    p.setFont("Helvetica-Bold", 12)
    p.line(60,188,220,188)
    p.drawString(60,175, nombre_rrhh)
    p.drawString(60,160, cargo_certificaciones)

    #FOOTER
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.gray)
    p.drawString(95,60, f'NIT: {nit_empresa} - Dirección: {direccion_empresa}, {ciudad_empresa} - Teléfono: {telefono_empresa}')
    p.drawString(225,45, f'e-mail: {email_empresa}')


    # Configuración del documento PDF
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response