from django.shortcuts import render,redirect

from io import BytesIO
from django.http import HttpResponse

## agregadas por manuel 
from io import BytesIO
from xhtml2pdf import pisa
from apps.components.workcertificategenerator import workcertificategenerator , workcertificatedownload
from django.contrib import messages
from apps.common.models import  Certificaciones , Contratos
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required


def get_empleado_name(empleado):
    papellido = empleado.get('idempleado__papellido', '') if empleado.get('idempleado__papellido') is not None else ""
    sapellido = empleado.get('idempleado__sapellido', '') if empleado.get('idempleado__sapellido') is not None else ""
    pnombre = empleado.get('idempleado__pnombre', '') if empleado.get('idempleado__pnombre') is not None else ""
    snombre = empleado.get('idempleado__snombre', '') if empleado.get('idempleado__snombre') is not None else ""
    return f"{papellido} {sapellido} {pnombre} {snombre}"


@login_required
@role_required('employee')
def vista_certificaciones(request):
    """
    Muestra al empleado una vista interactiva para gestionar sus certificaciones laborales.

    Esta vista permite al usuario seleccionar un contrato y ver las certificaciones asociadas. 
    Según el estado del contrato (activo o terminado), se cargan opciones diferentes para generar certificados.
    También se formatea la información para presentarla de manera clara en la interfaz.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP del navegador. Contiene la sesión del usuario y parámetros GET.

    Returns
    -------
    HttpResponse
        Renderiza la plantilla 'employees/certificaciones_laborales.html' con los datos del contrato y certificaciones.

    See Also
    --------
    Certificaciones : Modelo que representa los certificados laborales generados.
    Contratos : Modelo que contiene información sobre los contratos del empleado.
    get_empleado_name : Función auxiliar para formatear el nombre completo del empleado.

    Notes
    -----
    - Solo accesible para empleados autenticados.
    - Si el empleado tiene un solo contrato, se selecciona automáticamente.
    - Se ajustan las opciones del select según si el contrato está activo o liquidado.
    - Los valores de salario se formatean en estilo colombiano (puntos como separador de miles).
    """

    usuario = request.session.get('usuario', {})
    select_data = {}
    ESTADOS_CONTRATO = {
        1: "ACTIVO",
        2: "TERMINADO"
    }
    
    ide = usuario['idempleado']
    selected_empleado = request.GET.get('contrato')
    lista_certificaciones = []
    select = None
    
    
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
    
    cont = len(contratos)
    
    if cont == 1 : 
        selected_empleado = contratos[0]['idcontrato']    
    
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
            certi_all = Certificaciones.objects.filter(idcontrato_id=selected_empleado).values(
                'idcert', 
                'idcontrato__idempleado__papellido',
                'idcontrato__idempleado__pnombre',
                'idcontrato__idempleado__snombre',
                'idcontrato__idempleado__sapellido',
                'destino',
                'fecha',
                'cargo__nombrecargo',
                'salario',
                'tipocontrato',
                'promediovariable',
                'tipocertificacion'
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
                    'cargo': certi['cargo__nombrecargo'],
                    'tipo': certi['tipocontrato'],
                    'promedio': certi['promediovariable'],
                    'tipocerti': certi['tipocertificacion'],
                }

                lista_certificaciones.append(certi_data)
    
    
    
    return render(request, 'employees/certificaciones_laborales.html', {
        'contratos': contratos,
        'certificaciones': lista_certificaciones,
        'select': select,
        'select_data': select_data ,
        'selected_empleado':selected_empleado,
        'cont':cont
        
    })




@login_required
@role_required('employee')
def generateworkcertificate(request):
    """
    Genera un certificado laboral en formato PDF según los datos enviados por el usuario.

    Esta vista recibe los datos del formulario POST y genera un PDF con el contenido de un certificado laboral. 
    Usa una plantilla HTML y convierte el contenido a PDF con `xhtml2pdf`.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP del navegador. Se espera que contenga los campos 'empleado', 'contrato', 
        'data_input' y 'data_model' en el método POST.

    Returns
    -------
    HttpResponse
        PDF renderizado con el certificado, enviado en línea al navegador.

    See Also
    --------
    workcertificategenerator : Función que genera el contexto necesario para el certificado.

    Notes
    -----
    - Solo accesible para usuarios con rol `employee`.
    - El contenido se genera con base en una plantilla HTML ('workcertificatework.html').
    - Se usa `xhtml2pdf` (pisa) para convertir HTML a PDF.
    - En caso de error, se muestra un mensaje de error y se redirige a la vista de certificaciones.
    """

    try:
        if request.method == 'POST':
            empleado_id = request.POST.get('empleado')
            contrato_id = request.POST.get('contrato')
            data_input = request.POST.get('data_input')
            data_model = request.POST.get('data_model')
            
            context = workcertificategenerator( contrato_id , data_input ,data_model)
            
            
            
            html_string = render(request, './html/workcertificatework.html', context).content.decode('utf-8')
            
            pdf = BytesIO()
            pisa_status = pisa.CreatePDF(html_string, dest=pdf)
            pdf.seek(0)

            if pisa_status.err:
                return HttpResponse('Error al generar el PDF', status=400)

            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="Certificado.pdf"'
            
            return response
    
    except Exception as e:
        messages.error(request, 'Ocurrio un error inesperado')
        print(e)
        return redirect('employees:certificaciones')

@login_required
@role_required('employee')
def certificatedownload(request,idcert):
    """
    Descarga un certificado laboral previamente generado según su ID.

    Esta vista recupera los datos de un certificado ya existente y genera un PDF desde una plantilla HTML. 
    El archivo PDF se abre en el navegador.

    Parameters
    ----------
    request : HttpRequest
        Solicitud del navegador para descargar el certificado.

    idcert : int
        ID del certificado que se desea visualizar en PDF.

    Returns
    -------
    HttpResponse
        PDF renderizado del certificado laboral.

    See Also
    --------
    workcertificatedownload : Función que prepara el contexto del certificado según su ID.

    Notes
    -----
    - Solo accesible para empleados autenticados.
    - En caso de error, se muestra un mensaje y se redirige al listado de certificados.
    - Utiliza la plantilla HTML 'workcertificatework.html'.
    """

    try:
        context = workcertificatedownload(idcert)
        html_string = render(request, './html/workcertificatework.html', context).content.decode('utf-8')
        
        pdf = BytesIO()
        pisa_status = pisa.CreatePDF(html_string, dest=pdf)
        pdf.seek(0)

        if pisa_status.err:
            return HttpResponse('Error al generar el PDF', status=400)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="Certificado.pdf"'
        
        return response
    
    except Exception as e:
        messages.error(request, 'Ocurrio un error inesperado')
        print(e)
        return redirect('employees:workcertificate')
    


