from django.shortcuts import render,redirect
from apps.common.models  import Contratos , Contratosemp , Certificaciones
from apps.components.datacompanies import datos_cliente
from django.http import HttpResponse, HttpResponseRedirect
from io import BytesIO
from xhtml2pdf import pisa
from django.http import JsonResponse
from apps.components.workcertificategenerator import workcertificategenerator , workcertificatedownload
from django.contrib import messages
from django.db.models.functions import Coalesce
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required



# paso 1 filtrado de personal              #
# paso 2 generar nuevo certificado         #
# paso 3 descargar                         #

def get_empleado_name(empleado):
    papellido = empleado.get('idempleado__papellido', '') if empleado.get('idempleado__papellido') is not None else ""
    sapellido = empleado.get('idempleado__sapellido', '') if empleado.get('idempleado__sapellido') is not None else ""
    pnombre = empleado.get('idempleado__pnombre', '') if empleado.get('idempleado__pnombre') is not None else ""
    snombre = empleado.get('idempleado__snombre', '') if empleado.get('idempleado__snombre') is not None else ""
    return f"{papellido} {sapellido} {pnombre} {snombre}"




@login_required
@role_required('company')
def workcertificate(request):
    """
    Vista para filtrar empleados y visualizar certificados laborales generados.

    Esta vista permite a usuarios autenticados con el rol 'company' seleccionar un empleado, ver sus contratos y,
    dependiendo del contrato seleccionado, visualizar los certificados laborales existentes. Según el estado del contrato 
    (activo o terminado), se muestran diferentes opciones de generación de certificados, incluyendo tipos de salario.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP. Puede incluir parámetros GET como 'empleado' (ID del empleado) y 
        'contrato' (ID del contrato), utilizados para filtrar la información que se mostrará.

    Returns
    -------
    HttpResponse
        Devuelve la plantilla HTML 'companies/workcertificate.html' con el contexto necesario para 
        mostrar empleados, contratos, certificados generados y opciones de salario.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol 'company'. La vista proporciona datos clave para los pasos 
    de generación y descarga de certificados laborales. Usa `Contratosemp`, `Contratos` y `Certificaciones` como modelos principales.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    empleados = []
    SALARIO_CHOICES = []
    contratos = {}
    ESTADOS_CONTRATO = {
        1: "ACTIVO",
        2: "TERMINADO"
    }
    
    selected_empleado = request.GET.get('empleado')
    selected_Contrato = request.GET.get('contrato')
    
    if selected_empleado : 
        contratos_sin = Contratos.objects.filter(idempleado=selected_empleado).values('cargo__nombrecargo', 'fechainiciocontrato', 'fechafincontrato', 'estadocontrato', 'idcontrato')
        contratos = []

        for con in contratos_sin:
            estado_contrato = ESTADOS_CONTRATO.get(con['estadocontrato'], "")
            fechafincontrato = f"{con['fechafincontrato']}" if con['fechafincontrato'] is not None else ""
            contrato = {
                'cc': f"{con['cargo__nombrecargo']} - {con['fechainiciocontrato']} {estado_contrato}  {fechafincontrato} ",
                'idcontrato': con['idcontrato']
            }
            contratos.append(contrato)
    
    
    if selected_Contrato : 
        if estado_contrato == 'ACTIVO' :
            SALARIO_CHOICES = [
                ('1', 'Con salario básico'),
                ('2', 'Con salario promedio'),
                ('3', 'Sin salario'),
            ]
        else:
            SALARIO_CHOICES = [
                ('4','Contrato Liquidado'),
            ]
        
        
        certi_all = Certificaciones.objects.filter(idcontrato__idcontrato=selected_Contrato).select_related('idcontrato__idempleado').values('idcert', 
                                                                                                                        'idcontrato__idempleado__papellido',
                                                                                                                        'idcontrato__idempleado__pnombre',
                                                                                                                        'idcontrato__idempleado__snombre',
                                                                                                                        'idcontrato__idempleado__sapellido',
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

            empleados.append(certi_data)
    
    empleados_select = Contratosemp.objects.filter( id_empresa__idempresa =  idempresa ).order_by('papellido').values('pnombre', 'snombre', 'papellido', 'sapellido', 'idempleado')
    
    for emp in empleados_select:
        emp['pnombre'] = emp['pnombre'] if emp['pnombre'] is not None else ""
        emp['snombre'] = emp['snombre'] if emp['snombre'] is not None else ""
        emp['papellido'] = emp['papellido'] if emp['papellido'] is not None else ""
        emp['sapellido'] = emp['sapellido'] if emp['sapellido'] is not None else ""
    
    cont = len(contratos)
    
    context = {
        'empleados_select': empleados_select,
        'selected_Contrato':selected_Contrato,
        'contratos': contratos,
        'cont':cont,
        'selected_empleado': selected_empleado,
        'empleados': empleados,
        'salario_choices' : SALARIO_CHOICES,
    }
    
    return render(request, 'companies/workcertificate.html', context)


@login_required
@role_required('company')
def generateworkcertificate(request):
    """
    Vista para generar un nuevo certificado laboral en formato PDF.

    Esta vista procesa una solicitud POST para generar un certificado laboral, utilizando datos enviados por 
    formulario, incluyendo el contrato seleccionado, la plantilla y el contenido específico del certificado. 
    Usa la función `workcertificategenerator` para construir el contenido dinámico del certificado.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP con método POST. Se esperan los campos:
        - 'contrato' (ID del contrato a certificar)
        - 'data_input' (datos personalizados)
        - 'data_model' (tipo o plantilla del certificado)

    Returns
    -------
    HttpResponse
        Devuelve un archivo PDF renderizado en el navegador si la generación es exitosa.
        En caso de error, redirige a la vista 'workcertificate' y muestra un mensaje de error.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol 'company'.
    Utiliza `xhtml2pdf` para generar el PDF a partir de la plantilla HTML 'workcertificatework.html'.
    """

    
    try:
        if request.method == 'POST':
            contrato_id = request.POST.get('contrato')
            data_input = request.POST.get('data_input')
            data_model = request.POST.get('data_model')
            context = workcertificategenerator(contrato_id , data_input ,data_model)
            
            
            
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
        return redirect('companies:workcertificate')
    
    
@login_required
@role_required('company')  
def certificatedownload(request,idcert):
    """
    Vista para descargar un certificado laboral previamente generado.

    Esta vista permite a usuarios autenticados descargar un certificado laboral ya existente en formato PDF. 
    Se utiliza el identificador del certificado para recuperar la información y renderizar el documento 
    a través de la plantilla HTML correspondiente.

    Parameters
    ----------
    request : HttpRequest
        Solicitud HTTP estándar. El método puede ser GET o POST.
    
    idcert : int
        ID del certificado que se desea descargar.

    Returns
    -------
    HttpResponse
        Devuelve un archivo PDF renderizado directamente en el navegador.
        Si ocurre un error durante la generación, redirige a la vista 'workcertificate' con un mensaje de error.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol 'company'.
    La función auxiliar `workcertificatedownload` prepara el contexto necesario para la plantilla HTML.
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
        return redirect('companies:workcertificate')
    
    


