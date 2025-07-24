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

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.units import cm
import time
from reportlab.pdfgen import canvas

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
    
    context = genera_comprobante(idnomina, idcontrato)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    # Encabezado empresa
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(width / 2, height - 25, context['empresa'])
    p.setFont("Helvetica", 8)
    p.drawCentredString(width / 2, height - 35, context['nit'])
    p.drawCentredString(width / 2, height - 45, context['web'])

    # Línea horizontal
    p.setStrokeColor(colors.grey)
    p.setLineWidth(0.5)
    p.line(35, height - 60, width - 35, height - 60)

    # Logo
    try:
        logo = ImageReader(f"static/img/{context['logo']}")
        logo_width = 150
        logo_height = 50
        p.drawImage(logo, 35, height - 55, width=logo_width, height=logo_height,
                    preserveAspectRatio=True, mask='auto')
    except:
        pass

    # Subtítulo
    p.setFont("Courier-Bold", 15)
    p.drawCentredString(width / 2, height - 90, "Comprobante de Nómina")

    y = height - 120
# ---------------------- Tabla 1: Empleado ----------------------
    tabla1 = [
        ["Empleado", "Identificación", "Contrato", "Nómina"],
        [context['nombre_completo'], context['cc'], context['idcon'], context['idnomi']]
    ]

    tabla = Table(tabla1, colWidths=[8*cm, 4*cm, 4*cm, 4*cm], rowHeights=20)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b9c1c4")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    tabla.wrapOn(p, width, y)
    tabla.drawOn(p, 22, y - 40)
    y -= 40

    # ---------------------- Tabla 2: Cargo y salario ----------------------
    tabla2 = [
        ["Fecha Ingreso", "Cargo", "Salario", "Cuenta"],
        [context['fecha1'], context['cargo'], context['salario'], context['cuenta']]
    ]

    tabla = Table(tabla2, colWidths=[4*cm, 8*cm, 4*cm, 4*cm], rowHeights=20)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b9c1c4")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    tabla.wrapOn(p, width, y)
    tabla.drawOn(p, 22, y - 40)
    y -= 40

    # # ---------------------- Tabla 3: Costos y entidades ----------------------
    tabla3 = [
        ["Centro de Costo", "Periodo de Pago", "Salud", "Pensión"],
        [context['ccostos'], context['periodos'], str(context['eps']), str(context['pension'])]
    ]

    tabla = Table(tabla3, colWidths=[5*cm, 8*cm, 3.5*cm, 3.5*cm], rowHeights=20)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b9c1c4")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    tabla.wrapOn(p, width, y)
    tabla.drawOn(p, 22, y - 40)



    # # ---------------------- Tabla 4: Ingresos y Deducciones ----------------------
    
    encabezado_ingresos = [['INGRESOS', '', '', '']]
    filas_ingresos = []

    devengados = context['dataDevengado']
    for ingreso in devengados:
        fila = [
            ingreso.idconcepto.codigo,
            ingreso.nombreconcepto if ingreso else '',
            ingreso.cantidad if ingreso else '',
            f"{str(ingreso.valor).replace('.', ',')}" if ingreso else '',
        ]
        filas_ingresos.append(fila)

    # Rellenar hasta 15 filas (sin contar el encabezado)
    while len(filas_ingresos) < 15:
        filas_ingresos.append(['', '', '', ''])

    tabla_ingresos = encabezado_ingresos + filas_ingresos

    # DEDUCCIONES
    encabezado_descuentos = [['DEDUCCIONES', '', '', '']]
    filas_descuentos = []

    descuentos = context['dataDescuento']
    for descuento in descuentos:
        fila = [
            descuento.idconcepto.codigo,
            descuento.nombreconcepto if descuento else '',
            descuento.cantidad if descuento else '',
            f"{str(descuento.valor).replace('.', ',')}" if descuento else '',
        ]
        filas_descuentos.append(fila)

    # Rellenar hasta 15 filas
    while len(filas_descuentos) < 15:
        filas_descuentos.append(['', '', '', ''])

    tabla_descuentos = encabezado_descuentos + filas_descuentos

    # Columnas
    col_widths = [1*cm, 5*cm, 2*cm, 2*cm]

    # Crear tablas
    table_ingresos = Table(tabla_ingresos, colWidths=col_widths)
    table_descuentos = Table(tabla_descuentos, colWidths=col_widths)

    # Estilo común
        
    estilo_tabla = TableStyle([
        ('SPAN', (0, 0), (-1, 0)),
        # Encabezado gris claro sin colores si prefieres: eliminalo
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#b9c1c4")),
        
        ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # Alineación general
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),# Alinear concepto a la izquierda
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),# Alinear cantidad a la derecha
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'), # Alinear valor a la derecha

        # Si no quieres ninguna línea ni color:
        # (simplemente omite las siguientes líneas o comenta)
        ('LINEBEFORE', (1, 0), (-1, -1), 0.5, colors.black),
        ('LINEAFTER', (0, 0), (-2, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
    ])
    table_ingresos.setStyle(estilo_tabla)
    table_descuentos.setStyle(estilo_tabla)

    # Posiciones
    w_i, h_i = table_ingresos.wrap(0, 0)
    w_d, h_d = table_descuentos.wrap(0, 0)

    bottom_y = height - 250
    table_ingresos.drawOn(p, x=22, y=bottom_y - h_i)
    table_descuentos.drawOn(p, x=306, y=bottom_y - h_d)
    

    # ---------------------- Tabla 5: Totales ----------------------

    tabla5 = [
        ['', f"Total Ingresos:", '', context['sumadataDevengado'], '', f"Total Deducciones: ", '', context['sumadataDescuento']],
        ['', 'Total a Pagar:', '', context['total'], '', '', '', '']
    ]

    col_widths = [1*cm, 5*cm, 1*cm, 3*cm, 1*cm, 5*cm, 1*cm, 3*cm]

    tabla = Table(tabla5, colWidths=col_widths, rowHeights=18)

    tabla.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.8, colors.black),

        # Encabezado con spans bien colocado
        # Colores
        ('BACKGROUND', (0, 0), (3, 0), colors.HexColor("#b9c1c4")),
        ('BACKGROUND', (4, 0), (7, 0), colors.HexColor("#b9c1c4")),
        ('BACKGROUND', (0, -1), (2, -1), colors.HexColor("#81DAF5")),

        ('FONTNAME', (0, 0), (-1, 1), 'Courier-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        
        
        ('ALIGN', (3, 0), (3, 0), 'RIGHT'),  # sumadataDevengado
        ('ALIGN', (7, 0), (7, 0), 'RIGHT'),  # sumadataDescuento
        ('ALIGN', (3, 1), (3, 1), 'RIGHT'),  # total
    
    ]))

    tabla.wrapOn(p, width, y)
    tabla.drawOn(p, 22, y - 390)
    
    
    # Footer institucional
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.grey)
    p.drawCentredString(width / 2, 15, "Outsourcing de Nómina ::: www.nomiweb.co ::: Summa BPO SAS")


    ## data unica 
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    nombre_archivo = f'Certificado_{context["cc"]}_{fecha_actual}.pdf'
    
    # Finalizar PDF
    p.showPage()
    p.setTitle(nombre_archivo)
    p.setAuthor("Nomiweb")
    p.setSubject("Comprobante de Nomina {context['cc']}")
    p.setCreator("Sistema Nomiweb")
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
    response.write(pdf)
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



