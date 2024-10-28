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
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    empleados = []
    contratos = {}
    
    ESTADOS_CONTRATO = {
        1: "ACTIVO",
        2: "TERMINADO"
    }
    
    selected_empleado = request.GET.get('empleado')
    
    if selected_empleado:
        certi_all = Certificaciones.objects.filter(idcontrato__idempleado=selected_empleado).select_related('idcontrato__idempleado').values('idcert', 
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
        
        contratos_sin = Contratos.objects.filter(idempleado=selected_empleado).values('cargo', 'fechainiciocontrato', 'fechafincontrato', 'estadocontrato', 'idcontrato')
        contratos = []
        
        
        for con in contratos_sin:
            estado_contrato = ESTADOS_CONTRATO.get(con['estadocontrato'], "")
            fechafincontrato = f"{con['fechafincontrato']}" if con['fechafincontrato'] is not None else ""
            contrato = {
                'cc': f"{con['cargo']} - {con['fechainiciocontrato']} {estado_contrato}  {fechafincontrato} ",
                'idcontrato': con['idcontrato']
            }
            contratos.append(contrato)
            

        
    else:
        certi_all = []
        contratos = None
    
    empleados = []
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
        'contratos': contratos,
        'cont':cont,
        'selected_empleado': selected_empleado,
        'empleados': empleados
    }
    
    return render(request, 'companies/workcertificate.html', context)


@login_required
@role_required('company')
def generateworkcertificate(request):
    
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
        return redirect('companies:workcertificate')
    
    
@login_required
@role_required('company')  
def certificatedownload(request,idcert):

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
    
    


