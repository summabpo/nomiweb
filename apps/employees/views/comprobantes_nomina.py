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
        nominas = Nomina.objects.filter(idcontrato=selected_contrato_id).order_by('-idnomina')
    elif cont == 1:
        # Si solo hay un contrato, obtener las nóminas para ese contrato
        nominas = Nomina.objects.filter(idcontrato=contratos[0]['idcontrato']).order_by('-idnomina')
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
    ide = request.session.get('idempleado',{})
    context = genera_comprobante(idnomina,idcontrato,ide)
    
    
            
            
            
    html_string = render(request, './html/payrollcertificate.html', context).content.decode('utf-8')
    
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=pdf)
    pdf.seek(0)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=400)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Certificado.pdf"'
    
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


def vista_certificaciones(request):
    select_data = {}
    ESTADOS_CONTRATO = {
        1: "ACTIVO",
        2: "TERMINADO"
    }
    
    ide = request.session.get('idempleado', {})
    selected_empleado = request.GET.get('contrato')
    lista_certificaciones = []
    select = None
    
    if selected_empleado:
        auxcontrato = Contratos.objects.filter(idcontrato=selected_empleado).values('estadocontrato')
        if auxcontrato.exists():
            estado_contrato = auxcontrato[0]['estadocontrato']
            
            if estado_contrato == 1:
                select_data = {
                    '1': 'Con salario básico',
                    '2': 'Con salario promedio',
                    '3': 'Sin salario',
                }
            elif estado_contrato == 2:
                select_data = {
                    '4': 'Contrato Liquidado',
                }
            else:
                select_data = {}
            
            select = True
            certi_all = Certificaciones.objects.filter(idcontrato=selected_empleado).values(
                'idcert', 
                'idempleado__papellido',
                'idempleado__pnombre',
                'idempleado__snombre',
                'idempleado__sapellido',
                'destino',
                'fecha',
                'cargo',
                'salario',
                'tipocontrato',
                'promediovariable'
            )
            
            for certi in certi_all:
                nombre_empleado = get_empleado_name(certi)
                salario = "{:,.0f}".format(certi['salario']).replace(',', '.')
                
                certi_data = {
                    'idcert': certi['idcert'],
                    'empleado': nombre_empleado,
                    'destino': certi['destino'],
                    'Salario': salario,
                    'fecha': certi['fecha'],
                    'cargo': certi['cargo'],
                    'tipo': certi['tipocontrato'],
                    'promedio': certi['promediovariable'],
                }

                lista_certificaciones.append(certi_data)
    
    # contratos
    contratos_sin = Contratos.objects.filter(idempleado__idempleado=ide)    
    contratos = []
    
    for con in contratos_sin:
        estado_contrato = ESTADOS_CONTRATO.get(con.estadocontrato, "")
        fechafincontrato = f"{con.fechafincontrato}" if con.fechafincontrato is not None else ""
        contrato = {
            'cc': f"{con.cargo} - {con.fechainiciocontrato} {estado_contrato} {fechafincontrato}",
            'idcontrato': con.idcontrato
        }
        
        contratos.append(contrato)
    
    return render(request, 'employees/certificaciones_laborales.html', {
        'contratos': contratos,
        'certificaciones': lista_certificaciones,
        'select': select,
        'select_data': select_data ,
        'selected_empleado':selected_empleado
    })






