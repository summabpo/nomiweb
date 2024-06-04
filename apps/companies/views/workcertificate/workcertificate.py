from django.shortcuts import render,redirect
from apps.companies.models import Contratos , Contratosemp
from apps.components.datacompanies import datos_cliente
from django.http import HttpResponse
from io import BytesIO
from xhtml2pdf import pisa
from django.http import JsonResponse



# paso 1 filtrado de personal              #
# paso 2 generar nuevo certificado         #
# paso 3 descargar                         #


def workcertificate(request):
    
    if request.method == 'POST':
        empleado_id = request.POST.get('empleado')
        contrato_id = request.POST.get('contrato')
        data_input = request.POST.get('data_input')
    
    
    
    contratos_empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre', 'fechainiciocontrato', 'cargo', 'salario', 'idcosto__nomcosto',
                'tipocontrato__tipocontrato', 'centrotrabajo__tarifaarl')

    empleados = []
    for contrato in contratos_empleados:
        nombre_empleado = f"{contrato['idempleado__papellido']} {contrato['idempleado__pnombre']} {contrato['idempleado__snombre']}"
        salario = "{:,.0f}".format(contrato['salario']).replace(',', '.')

        contrato_data = {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': nombre_empleado,
            'fechainiciocontrato': contrato['fechainiciocontrato'],
            'cargo': contrato['cargo'],
            'salario': salario,
            'centrocostos': contrato['idcosto__nomcosto'],
            'tipocontrato': contrato['tipocontrato__tipocontrato'],
            'tarifaARL': contrato['centrotrabajo__tarifaarl'],
        }

        empleados.append(contrato_data)   
    
    
    
    empleados_select = Contratosemp.objects.all()
    
    # Si hay un empleado seleccionado, cargar sus contratos
    contratos = None
    selected_empleado = request.GET.get('empleado')
    if selected_empleado:
        contratos = Contratos.objects.filter(idempleado=selected_empleado)
    
    context = {
        'empleados_select': empleados_select,
        'contratos': contratos,
        'selected_empleado': selected_empleado,
        'empleados':empleados
    }
    
    
    return render(request, 'companies/workcertificate.html', context)
    


def cargar_contratos_view(request):
    empleado_id = request.GET.get('empleado')
    contratos = Contratos.objects.filter(idempleado=empleado_id).values('idcontrato', 'cargo', 'fechafincontrato')
    return JsonResponse(list(contratos), safe=False)



def workcertificate2(request):
    contratos_empleados = Contratos.objects\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre', 'fechainiciocontrato', 'cargo', 'salario', 'idcosto__nomcosto',
                'tipocontrato__tipocontrato', 'centrotrabajo__tarifaarl')

    empleados = []
    for contrato in contratos_empleados:
        nombre_empleado = f"{contrato['idempleado__papellido']} {contrato['idempleado__pnombre']} {contrato['idempleado__snombre']}"
        salario = "{:,.0f}".format(contrato['salario']).replace(',', '.')

        contrato_data = {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': nombre_empleado,
            'fechainiciocontrato': contrato['fechainiciocontrato'],
            'cargo': contrato['cargo'],
            'salario': salario,
            'centrocostos': contrato['idcosto__nomcosto'],
            'tipocontrato': contrato['tipocontrato__tipocontrato'],
            'tarifaARL': contrato['centrotrabajo__tarifaarl'],
        }

        empleados.append(contrato_data)        
    return render(request, 'companies/workcertificate.html' , {'empleados': empleados} )

def generateworkcertificate(request):
    if request.method == 'POST':
        empleado_id = request.POST.get('empleado')
        contrato_id = request.POST.get('contrato')
        data_input = request.POST.get('data_input')
        data = request.POST.get('data')
        datosc = datos_cliente()
                
        if not data:
            try:
                empleado = Contratosemp.objects.get( idempleado = empleado_id )
            except Contratosemp.DoesNotExist:
                return HttpResponse('No se encontró ningún empleado con el documento de identidad proporcionado.', status=404)
            except Contratosemp.MultipleObjectsReturned:
                return HttpResponse('Múltiples empleados encontrados con el documento de identidad proporcionado.', status=400)
                
            try:
                contrato = Contratos.objects.get(idcontrato = contrato_id)
            except Contratos.DoesNotExist:
                return HttpResponse('No se encontró ningún contrato asociado al empleado.', status=404)
            
            
            context = {
                ## empresa 
                'empresa':datosc['nombre_empresa'],
                'rrhh':datosc['nombre_rrhh'],
                'nit': datosc['nit_empresa'],
                'direccion':datosc['direccion_empresa'],
                'ciudad':datosc['ciudad_empresa'],
                'web':datosc['website_empresa'],
                'telefono':datosc['telefono_empresa'],
                'email ': datosc['email_empresa'],
                'logo' : datosc['logo_empresa'],
                'firma' : datosc['firma_certificaciones'],
                
                
                ## empleado
                'titulo': 'Texto1',
                'codigo' : 'COD3',
                'nombre' : f"{empleado.papellido} {empleado.sapellido} {empleado.pnombre} {empleado.snombre}",
                'identificacion': empleado.docidentidad,
                'fecha':contrato.fechainiciocontrato,
                'cargo':contrato.cargo,
                'sueldo': "{:,.0f}".format(contrato.salario).replace(',', '.'),
                'tipoc':contrato.tipocontrato.tipocontrato , 
                
            }
            
            
        else:
            try:
                empleado = Contratosemp.objects.get(docidentidad=data)
            except Contratosemp.DoesNotExist:
                return HttpResponse('No se encontró ningún empleado con el documento de identidad proporcionado.', status=404)
            except Contratosemp.MultipleObjectsReturned:
                return HttpResponse('Múltiples empleados encontrados con el documento de identidad proporcionado.', status=400)
                
            try:
                contrato = Contratos.objects.filter(idempleado=empleado).latest('fechainiciocontrato')
            except Contratos.DoesNotExist:
                return HttpResponse('No se encontró ningún contrato asociado al empleado.', status=404)
            
            context = {
                ## empresa 
                'empresa':datosc['nombre_empresa'],
                'rrhh':datosc['nombre_rrhh'],
                'nit': datosc['nit_empresa'],
                'direccion':datosc['direccion_empresa'],
                'ciudad':datosc['ciudad_empresa'],
                'web':datosc['website_empresa'],
                'telefono':datosc['telefono_empresa'],
                'email ': datosc['email_empresa'],
                'logo' : datosc['logo_empresa'],
                'firma' : datosc['firma_certificaciones'],
                
                
                ## empleado
                'titulo': 'Texto1',
                'codigo' : 'COD3',
                'nombre' : f"{empleado.papellido} {empleado.sapellido} {empleado.pnombre} {empleado.snombre}",
                'identificacion': empleado.docidentidad,
                'fecha':contrato.fechainiciocontrato,
                'cargo':contrato.cargo,
                'sueldo': "{:,.0f}".format(contrato.salario).replace(',', '.'),
                'tipoc':contrato.tipocontrato.tipocontrato , 
                
            }

        
        # id_cliente : datosc['id_cliente']
        # cargo_certificaciones : datosc['cargo_certificaciones']
        # firma_certificaciones : datosc['firma_certificaciones']
        
        
        html_string = render(request, './html/workcertificatework.html', context).content.decode('utf-8')
        
        pdf = BytesIO()
        pisa_status = pisa.CreatePDF(html_string, dest=pdf)
        pdf.seek(0)

        if pisa_status.err:
            return HttpResponse('Error al generar el PDF', status=400)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="mi_documento.pdf"'
        return response
    else: 
        return redirect('companies:workcertificate')


