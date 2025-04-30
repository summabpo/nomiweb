from django.shortcuts import render
from datetime import datetime
import datetime
from django.db.models import Sum
from io import BytesIO
from django.http import HttpResponse
import locale
from datetime import datetime
from io import BytesIO
from xhtml2pdf import pisa
from apps.components.payrollgenerate import genera_comprobante 
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.views.generic import  ListView

#models
from apps.common.models import Crearnomina, Nomina, Contratos
try:
    # Intenta usar el locale en español
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
except locale.Error:
    # Si no está disponible, usa una configuración neutral
    locale.setlocale(locale.LC_ALL, 'C')
    print("Advertencia: No se pudo configurar 'es_ES.UTF-8'. Usando 'C'.")




@login_required
@role_required('employee')
def listaNomina(request):
    """
    Muestra una lista de nóminas asociadas a un empleado según su contrato.

    Esta vista permite a un empleado visualizar sus nóminas disponibles. Los contratos activos o terminados
    asociados al empleado se recuperan y presentan para que el usuario seleccione uno. Dependiendo del contrato
    seleccionado, se muestran las nóminas correspondientes.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP del navegador. Contiene la sesión del usuario y parámetros GET para determinar el contrato seleccionado.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'employees/comprobantes.html' con la lista de nóminas disponibles y los contratos del empleado.

    Notes
    -----
    - Solo accesible para empleados autenticados.
    - Si el empleado tiene un solo contrato, se selecciona automáticamente.
    - Los contratos se formatean para incluir información sobre el cargo, estado y fechas de inicio y fin.
    """

    usuario = request.session.get('usuario', {})
    ide = usuario['idempleado']
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
    
    
@login_required
@role_required('employee')
def generatepayrollcertificate(request ,idnomina,idcontrato,):
    """
    Genera un certificado de nómina en formato PDF para un empleado y contrato específicos.

    Esta vista toma los datos de una nómina y contrato, los utiliza para generar un comprobante de nómina en formato PDF.
    El PDF se genera utilizando una plantilla HTML y se envía al navegador como un archivo descargable.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP del navegador. Contiene los parámetros POST necesarios para generar el certificado.
    idnomina : int
        ID de la nómina para la que se generará el certificado.
    idcontrato : int
        ID del contrato asociado con la nómina.

    Returns
    -------
    HttpResponse
        PDF del certificado de nómina generado.

    Notes
    -----
    - Solo accesible para empleados autenticados.
    - El nombre del archivo PDF incluye el nombre del contrato y la fecha actual.
    - En caso de error al generar el PDF, se muestra un mensaje de error y el código de estado 400.
    """

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







class ListaNominas(ListView):
    """
    Clase que muestra una lista paginada de nóminas para un contrato específico.

    Esta vista de clase hereda de ListView y muestra las nóminas asociadas a un contrato en particular. 
    Los registros se ordenan por ID de nómina y se presentan en formato paginado.

    Attributes
    ----------
    model : Nomina
        Modelo de datos asociado con la vista. En este caso, el modelo `Nomina` es utilizado para obtener los datos.
    template_name : str
        Nombre del archivo de plantilla que se utiliza para renderizar la respuesta.
    paginate_by : int
        Número de elementos a mostrar por página.
    context_object_name : str
        Nombre del contexto de la variable que contiene la lista de nóminas en la plantilla.
    ordering : str
        Campo por el cual se ordenarán las nóminas.

    Methods
    -------
    get_queryset()
        Recupera las nóminas asociadas al contrato del empleado para ser presentadas en la vista.
    """

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
    """
    Clase que muestra los detalles de los conceptos de una nómina.

    Esta vista de clase hereda de ListView y se utiliza para mostrar los conceptos detallados de una nómina específica,
    tales como devengados y descuentos. Además, proporciona los totales y el cálculo del neto a pagar. 

    Attributes
    ----------
    model : Nomina
        Modelo de datos asociado con la vista. En este caso, el modelo `Nomina` se utiliza para obtener los datos.
    context_object_name : str
        Nombre del contexto de la variable que contiene la lista de conceptos en la plantilla.
    template_name : str
        Nombre del archivo de plantilla que se utiliza para renderizar la respuesta.

    Methods
    -------
    nombreNomina()
        Obtiene el nombre de la nómina correspondiente.
    get_queryset()
        Recupera los conceptos detallados de la nómina según el contrato y la nómina seleccionada.
    totalDevengados()
        Calcula el total de los valores devengados en la nómina.
    totalDescuentos()
        Calcula el total de los descuentos aplicados en la nómina.
    netoPagar()
        Calcula el monto neto a pagar después de los descuentos.
    get_context_data(**kwargs)
        Devuelve el contexto adicional necesario para renderizar la plantilla, incluyendo los totales calculados.
    """

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



