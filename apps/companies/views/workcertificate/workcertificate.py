from django.shortcuts import render,redirect
from apps.companies.models import Contratos , Contratosemp
from apps.components.datacompanies import datos_cliente
from django.http import HttpResponse, HttpResponseRedirect
from io import BytesIO
from xhtml2pdf import pisa
from django.http import JsonResponse
from apps.components.workcertificategenerator import workcertificategenerator , workcertificatedownload
from django.contrib import messages
from apps.employees.models import Certificaciones




# paso 1 filtrado de personal              #
# paso 2 generar nuevo certificado         #
# paso 3 descargar                         #



def workcertificate(request):
    ESTADOS_CONTRATO = {
        1: "ACTIVO",
        2: "TERMINADO"
    }
    
    selected_empleado = request.GET.get('empleado')
    
    if selected_empleado:
        certi_all = Certificaciones.objects.filter(idempleado=selected_empleado).select_related('idempleado')
        contratos_sin = Contratos.objects.filter(idempleado=selected_empleado)
        contratos = []

        for con in contratos_sin:
            estado_contrato = ESTADOS_CONTRATO.get(con.estadocontrato, "")
            fechafincontrato = con.fechafincontrato if con.fechafincontrato is not None else ""
            contrato = {
                'cc': f"{con.cargo} - {con.fechainiciocontrato}  {fechafincontrato} {estado_contrato}",
                'idcontrato': con.idcontrato
            }
            contratos.append(contrato)
            

        
    else:
        certi_all = []
        contratos = None
    
    empleados = []
    for certi in certi_all:
        nombre_empleado = f"{certi.idempleado.papellido} {certi.idempleado.pnombre} {certi.idempleado.snombre}" 
        salario = "{:,.0f}".format(certi.salario).replace(',', '.')
        
        certi_data = {
            'idcert': certi.idcert,
            'empleado': nombre_empleado,
            'destino': certi.destino,
            'Salario': salario,
            'fecha': certi.fecha,
            'cargo': certi.cargo,
            'tipo': certi.tipocontrato,
            'promedio': certi.promediovariable,
        }

        empleados.append(certi_data)
    
    empleados_select = Contratosemp.objects.all().order_by('papellido')

    context = {
        'empleados_select': empleados_select,
        'contratos': contratos,
        'selected_empleado': selected_empleado,
        'empleados': empleados
    }
    
    return render(request, 'companies/workcertificate.html', context)



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
    
    


