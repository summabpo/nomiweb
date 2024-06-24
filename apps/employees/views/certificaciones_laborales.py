from django.shortcuts import render,redirect

from io import BytesIO
from django.http import HttpResponse

## agregadas por manuel 
from apps.employees.models import Contratos, Contratosemp
from io import BytesIO
from xhtml2pdf import pisa
from apps.components.workcertificategenerator import workcertificategenerator , workcertificatedownload
from django.contrib import messages
from apps.employees.models import  Certificaciones
from apps.components.decorators import custom_permission
from django.contrib.auth.decorators import login_required



def get_empleado_name(empleado):
    papellido = empleado.get('idempleado__papellido', '') if empleado.get('idempleado__papellido') is not None else ""
    sapellido = empleado.get('idempleado__sapellido', '') if empleado.get('idempleado__sapellido') is not None else ""
    pnombre = empleado.get('idempleado__pnombre', '') if empleado.get('idempleado__pnombre') is not None else ""
    snombre = empleado.get('idempleado__snombre', '') if empleado.get('idempleado__snombre') is not None else ""
    return f"{papellido} {sapellido} {pnombre} {snombre}"



@login_required
@custom_permission('employees')
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
    
    
    
    return render(request, 'employees/certificaciones_laborales.html', {
        'contratos': contratos,
        'certificaciones': lista_certificaciones,
        'select': select,
        'select_data': select_data ,
        'selected_empleado':selected_empleado,
        'cont':cont
        
    })




@login_required
@custom_permission('employees')
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
@custom_permission('employees')
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
    


