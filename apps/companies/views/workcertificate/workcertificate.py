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
    selected_empleado = request.GET.get('empleado')
    
    if selected_empleado:
        certi_all = Certificaciones.objects.filter(idempleado=selected_empleado).select_related('idempleado')
        contratos = Contratos.objects.filter(idempleado=selected_empleado)
    else:
        certi_all = Certificaciones.objects.all().select_related('idempleado')
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
    
    empleados_select = Contratosemp.objects.all()

    context = {
        'empleados_select': empleados_select,
        'contratos': contratos,
        'selected_empleado': selected_empleado,
        'empleados': empleados
    }
    
    return render(request, 'companies/workcertificate.html', context)



def cargar_contratos_view(request):
    empleado_id = request.GET.get('empleado')
    contratos = Contratos.objects.filter(idempleado=empleado_id).values('idcontrato', 'cargo', 'fechafincontrato')
    return JsonResponse(list(contratos), safe=False)





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
        return redirect('companies:workcertificate')
    
    


