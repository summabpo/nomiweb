from django.shortcuts import render,redirect
from datetime import datetime
import datetime
from typing import Any, Dict
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
from datetime import datetime

from django.contrib import messages
from io import BytesIO
from xhtml2pdf import pisa

# Create your views here.
from django.views.generic import  ListView, DetailView

#models
from apps.employees.models import Crearnomina, Nomina, Contratos, Contratosemp
locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

from apps.components.decorators import custom_permission
from apps.components.payrollgenerate import genera_comprobante 






def listaNomina(request):
    ide = request.session.get('idempleado')
    ESTADOS_CONTRATO = {
        1: "ACTIVO",
        2: "TERMINADO"
    }
    
    # Obtener todos los contratos del empleado
    contratos_sin = Contratos.objects.filter(idempleado__idempleado=ide)
    
    # Lista para almacenar los contratos formateados
    contratos = []
    
    for con in contratos_sin:
        estado_contrato = ESTADOS_CONTRATO.get(con.estadocontrato, "")
        fechafincontrato = con.fechafincontrato.strftime("%Y-%m-%d") if con.fechafincontrato else ""
        contrato = {
            'cc': f"{con.cargo} - {con.fechainiciocontrato} {estado_contrato} {fechafincontrato}",
            'idcontrato': con.idcontrato
        }
        contratos.append(contrato)
    
    # Contar el número de contratos
    cont = len(contratos)    
    # Obtener el contrato seleccionado, si existe
    selected_contrato_id = request.GET.get('contrato')
    if selected_contrato_id:
        nominas = Nomina.objects.distinct('idnomina').filter(idcontrato=selected_contrato_id).order_by('-idnomina')
    elif cont == 1:
        # Si solo hay un contrato, obtener las nóminas para ese contrato
        nominas = Nomina.objects.distinct('idnomina').filter(idcontrato=contratos[0]['idcontrato']).order_by('-idnomina')
    else:
        # En otros casos, no mostrar nóminas
        nominas = []
    
    return render(request, 'employees/comprobantes.html', {
        'nominas': nominas,
        'contratos': contratos,
        'selected_empleado': selected_contrato_id,
        'cont': cont
    })

def generatepayrollcertificate(request ,idnomina,idcontrato,):
    context = genera_comprobante(idnomina,idcontrato)
    
    
    html_string = render(request, './html/payrollcertificate.html', context).content.decode('utf-8')
    
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=pdf)
    pdf.seek(0)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=400)
    
    nombre_archivo = f'Certificado_{context["cc"]}_{fecha_actual}.pdf'

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
    
    return response

    
    
    # try:
    #     if request.method == 'POST':
            
            
    
    # except Exception as e:
    #     messages.error(request, 'Ocurrio un error inesperado')
    #     print(e)
    #     return redirect('companies:workcertificate')







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


# @custom_login_required
# @custom_permission('employees')


## copiar y elimiar 



