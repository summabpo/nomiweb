from datetime import datetime
import datetime
from typing import Any, Dict
from django.shortcuts import render
from django.db.models import Sum, F, Value, CharField
from django.db.models.functions import Concat
from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
import locale
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep, Color, black, lightblue, red
import imgkit


# Create your views here.
from django.views.generic import  ListView, DetailView

#models
from apps.employees.models import Crearnomina, Nomina, Contratos, Contratosemp
locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

from apps.components.decorators import custom_login_required ,custom_permission



idn = 499
idc = 3863
ide = 281

class ListaNominas(ListView):
    template_name = 'employees/comprobantes.html'
    paginate_by = 30
    context_object_name = 'nominas'
    model = Nomina
    ordering = 'idnomina'
    
    def get_queryset(self):
        #data = Nomina.objects.filter(idcontrato=2380).select_related('idnomina')
        #queryset = Nomina.objects.select_related('Crearnomina').values('idcontrato', 'idnomina', 'Crearnomina__nombrenomina')
        queryset = Nomina.objects.distinct('idnomina').filter(idcontrato=idc).order_by('-idnomina').select_related('idnomina')
        return queryset

class ListaConceptosNomina(ListView):
    model = Nomina
    context_object_name = 'conceptos'
    template_name = 'employees/recibo.html'

    def nombreNomina(self):
        nombrenomina = Crearnomina.objects.get(idnomina=idn).nombrenomina
        return nombrenomina

    def get_queryset(self):
        queryset = Nomina.objects.filter(idcontrato=idc, idnomina=idn).order_by('idconcepto')
        return queryset

    def totalDevengados(self):
        totaldevengados = Nomina.objects.filter(idcontrato=idc, idnomina=idn, valor__gt=0).aggregate(totaldevengados=Sum('valor'))['totaldevengados']
        return totaldevengados

    def totalDescuentos(self):
        totaldescuentos = Nomina.objects.filter(idcontrato=idc,idnomina=idn, valor__lt=0).aggregate(totaldescuentos=Sum('valor'))['totaldescuentos']
        return totaldescuentos

    def netoPagar(self):
        netoapagar = Nomina.objects.filter(idcontrato=idc,idnomina=idn).aggregate(netoapagar=Sum('valor'))['netoapagar']
        return netoapagar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['netoapagar'] = self.netoPagar()
        context['totaldevengados'] = self.totalDevengados()
        context['totaldescuentos'] = self.totalDescuentos()
        context['nombrenomina'] = self.nombreNomina()
        return context


@custom_login_required
@custom_permission('employees')
def genera_comprobante(request, idnomina, idcontrato):
        idc=idcontrato
        idn=idnomina
        idempleado_id = Contratos.objects.get(idcontrato=idc).idempleado_id
        ide=idempleado_id

        response = HttpResponse(content_type='application/pdf')
        d = datetime.datetime.today().strftime('%Y-%m-%d')
        response['Content-Disposition'] = f'inline; filename="{d}.pdf'

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        html_file = 'static/html/comprobante_nomina.html'
        img_file = 'static/img/comprobante.png'

        #Configuración de imgkit
        opciones = {
            'quiet': '',
            'width': '820',
            'height': '792',
        }

        #Convierte el HTML en una imagen
        imgkit.from_file(html_file, img_file, options=opciones)

        #Abre la imagen de fondo usando ImageReader de ReportLab
        imagen_fondo = ImageReader(img_file)

        #Define el tamaño de la página
        ancho_pagina, alto_pagina = letter

        #Dibuja la imagen de fondo en todas las páginas
        p.drawImage(imagen_fondo, 25, -90, ancho_pagina, alto_pagina)

        #data to print
        empleado = Contratosemp.objects.filter(idempleado = ide).annotate(empleado=Concat(
            F('papellido'),
            Value(' '),
            F('sapellido'),
            Value(' '),
            F('pnombre'),
            Value(' '),
            F('snombre'),
            output_field=CharField()
            )
        ).values('empleado').first()
        nombre_completo=empleado['empleado']

        dataDevengado = Nomina.objects.filter(idcontrato=idc, idnomina=idn, valor__gt=0).order_by('idconcepto')
        dataDescuento = Nomina.objects.filter(idcontrato=idc, idnomina=idn, valor__lt=0).order_by('idconcepto')
        logo = ImageReader('static/img/logo lecta.jpeg')
        #start pdf
        p.drawImage(logo, 20, 730, width=130, preserveAspectRatio=True, mask='auto')
        p.setFont("Helvetica",18,leading=None)
        p.setFillColor(lightblue)
        p.line(20,750,590,750)
        p.drawString(200,710,'Comprobante de Nómina')
        p.setFont("Helvetica",15,leading=None)
        p.setFillColor(black)
        p.drawString(120,670,'Empleado')
        p.setFont("Courier",10,leading=None)
        p.drawString(50,640, nombre_completo)

        x1 = 53
        y1 = 437
        #render data
        for obj in dataDevengado:
            p.setFont("Courier",9,leading=None)
            p.drawRightString(x1,y1-12,f"{obj.idconcepto}")
            p.drawString(x1 + 10,y1-12,f"{obj.nombreconcepto}")
            p.drawRightString(x1 + 177,y1-12,f"{obj.cantidad}")
            valor_formateado = locale.format_string("%0.0f", obj.valor, grouping=True, monetary=True)
            p.drawRightString(x1 + 244,y1-12,f"{valor_formateado}")
            y1 = y1 - 10
        y1 = 437
        for obj in dataDescuento:
            p.setFont("Courier",9,leading=None)
            p.drawRightString(x1 + 270,y1-12,f"{obj.idconcepto}")
            p.drawString(x1 + 280,y1-12,f"{obj.nombreconcepto}")
            p.drawRightString(x1 + 445,y1-12,f"{obj.cantidad}")
            valor_formateado = locale.format_string("%0.0f", obj.valor, grouping=True, monetary=True)
            p.drawRightString(x1 + 510,y1-12,f"{valor_formateado}")
            y1 = y1 - 10

        totalDevengados = Nomina.objects.filter(idcontrato=idc, idnomina=idn, valor__gt=0).aggregate(totalDevengados=Sum('valor'))['totalDevengados']
        devengadosFormateado=locale.format_string("%0.0f", totalDevengados, grouping=True, monetary=True)
        totalDescuentos = Nomina.objects.filter(idcontrato=idc,idnomina=idn, valor__lt=0).aggregate(totalDescuentos=Sum('valor'))['totalDescuentos']
        descuentosFormateado = locale.format_string("%0.0f", totalDescuentos, grouping=True, monetary=True)
        netoaPagar = Nomina.objects.filter(idcontrato=idc,idnomina=idn).aggregate(netoaPagar=Sum('valor'))['netoaPagar']
        netoFormateado = locale.format_string("%0.0f", netoaPagar, grouping=True, monetary=True)

        p.setFont("Courier",14,leading=None)
        p.drawRightString(300, 163,f"{devengadosFormateado}")
        p.drawRightString(580, 163,f"{descuentosFormateado}")
        p.drawRightString(480, 123,f"{netoFormateado}")

        p.setTitle(f'Report on {d}')
        p.showPage()
        p.save()
        
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        
        return response