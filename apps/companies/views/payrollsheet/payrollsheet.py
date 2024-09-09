from django.shortcuts import render
from apps.companies.models import Nomina , NominaComprobantes
from apps.components.humani import format_value
from io import BytesIO
from xhtml2pdf import pisa
from datetime import datetime
from django.http import HttpResponse
from apps.components.payrollgenerate import generate_summary
from apps.components.payrollgenerate import genera_comprobante 
from apps.components.mail import send_template_email2 ,send_template_email3
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from PyPDF2 import PdfMerger
from django.template.loader import render_to_string

def get_email_status(estado_email):
    if estado_email == 1:
        envio_email = 'Enviado'
    elif estado_email == 2:
        envio_email = 'Error'
    else:
        envio_email = 'Sin Enviar'

    return envio_email


@login_required
@role_required('entrepreneur')
def payrollsheet(request):
    #nominas = Nomina.objects.select_related('idnomina').values('idnomina__nombrenomina', 'idnomina').distinct().order_by('-idnomina')
    nominas = Nomina.objects.select_related('idnomina').values_list('idnomina__nombrenomina', 'idnomina').distinct().order_by('-idnomina')

    compects = []
    acumulados = {}

    selected_nomina = request.GET.get('nomina')
    if selected_nomina:
        compectos = Nomina.objects.filter(idnomina=selected_nomina)
        
        # Consulta 1: Total neto
        # neto = Nomina.objects.filter(idnomina=id_nomina).aggregate(Sum('valor'))['valor__sum'] or 0
        # # Consulta 2: Total ingresos
        # ingresos = Nomina.objects.filter(idnomina=id_nomina, valor__gt=0).aggregate(Sum('valor'))['valor__sum'] or 0
        # descuentos = neto - ingresos
        # # Consulta 3: Salario básico
        # basico = Nomina.objects.filter(idnomina=id_nomina, idconcepto__in=[1, 4]).aggregate(Sum('valor'))['valor__sum'] or 0
        # # Consulta 4: Transporte
        # transporte = Nomina.objects.filter(idnomina=id_nomina, idconcepto=2).aggregate(Sum('valor'))['valor__sum'] or 0
        # # Consulta 5: Extras
        # extras = Nomina.objects.filter(idnomina=id_nomina, conceptosdenomina__extras=1).aggregate(Sum('valor'))['valor__sum'] or 0
        # otrosing = ingresos - basico - extras - transporte
        # # Consulta 6: Aportes
        # aportes = Nomina.objects.filter(idnomina=id_nomina, conceptosdenomina__aportess=1).aggregate(Sum('valor'))['valor__sum'] or 0
        # # Consulta 7: Préstamos
        # prestamos = Nomina.objects.filter(idnomina=id_nomina, idconcepto=50).aggregate(Sum('valor'))['valor__sum'] or 0
        # otrosdesc = descuentos - prestamos - aportes
        # # Consulta 8: Estado email
        # estado_email = CrearNomina.objects.filter(idnomina=id_nomina).values_list('envio_email', flat=True).first()
        
        
        for data in compectos:
            
            docidentidad = data.idcontrato.idcontrato
            compribanten = NominaComprobantes.objects.get(idnomina = selected_nomina ,idcontrato = data.idcontrato.idcontrato )
            if docidentidad not in acumulados:
                acumulados[docidentidad] = {
                    'documento': docidentidad,
                    'nombre': f"{data.idempleado.papellido} {data.idempleado.sapellido} {data.idempleado.pnombre} {data.idempleado.snombre}",
                    'neto': 0,
                    'ingresos': 0,
                    'basico': 0,
                    'tpte': 0,
                    'extras': 0,
                    'aportess': 0,
                    'prestamos': 0,
                    'estado': get_email_status(compribanten.envio_email) ,
                    'nominaid': data.idnomina.idnomina,
                    'contratoid' :data.idcontrato.idcontrato,   
                }
            
            acumulados[docidentidad]['neto'] += data.valor
            acumulados[docidentidad]['ingresos'] += data.valor if data.valor > 0 else 0
            acumulados[docidentidad]['basico'] += data.valor if data.idconcepto.sueldobasico == 1 else 0
            acumulados[docidentidad]['tpte'] += data.valor if data.idconcepto.auxtransporte == 1 else 0
            acumulados[docidentidad]['extras'] += data.valor if data.idconcepto.extras == 1 else 0
            acumulados[docidentidad]['aportess'] += data.valor if data.idconcepto.aportess == 1 else 0
            acumulados[docidentidad]['prestamos'] += data.valor if data.idconcepto.idconcepto == 50 else 0
        
        compects = list(acumulados.values())

    for compect in compects:
        compect['descuentos'] = compect['neto'] - compect['ingresos']
        compect['otrosing'] = compect['ingresos'] - compect['basico'] - compect['extras'] - compect['tpte']
        compect['otrosdesc'] = compect['descuentos'] - compect['prestamos'] - compect['aportess']
        
        # Formatear los valores
        for key in ['neto', 'ingresos', 'basico', 'tpte', 'extras', 'aportess', 'prestamos', 'descuentos', 'otrosing', 'otrosdesc']:
            compect[key] = format_value(compect[key])

    return render(request, 'companies/payrollsheet.html', {
        'nominas': nominas,
        'compects': compects,
        'selected_nomina': selected_nomina,
    })



@login_required
@role_required('entrepreneur')
def generatepayrollsummary(request,idnomina):
    context = generate_summary(idnomina)
    
    html_string = render(request, './html/payrollsummary.html', context).content.decode('utf-8')
    
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=pdf)
    pdf.seek(0)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=400)
    
    nombre_archivo = f'Certificado_{idnomina}_{fecha_actual}.pdf'

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
    
    return response

@login_required
@role_required('entrepreneur')
def generatepayrollsummary2(request, idnomina):
    # Obtener los contratos únicos ordenados por apellido
    idcontratos_unicos = Nomina.objects.filter(idnomina=idnomina).order_by('idempleado__papellido').values_list('idcontrato', flat=True).distinct()
    
    # Crear un objeto para combinar PDFs
    merger = PdfMerger()
    
    for idcontrato in idcontratos_unicos:
        # Generar el contexto para cada contrato
        context = genera_comprobante(idnomina, idcontrato)
        
        # Renderizar el template a una cadena HTML
        html_string = render_to_string('./html/payrollcertificate.html', context)
        
        # Crear el PDF para cada documento
        pdf = BytesIO()
        pisa_status = pisa.CreatePDF(html_string, dest=pdf)
        pdf.seek(0)

        if pisa_status.err:
            return HttpResponse('Error al generar uno de los PDFs', status=400)
        
        # Agregar el PDF al merger
        merger.append(pdf)
    
    # Crear un archivo PDF final combinando todos los PDFs
    combined_pdf = BytesIO()
    merger.write(combined_pdf)
    combined_pdf.seek(0)
    
    # Crear el nombre del archivo con la fecha actual
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    nombre_archivo = f'Certificado_{idnomina}_{fecha_actual}.pdf'

    # Preparar la respuesta HTTP con el PDF final
    response = HttpResponse(combined_pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
    
    return response


@login_required
@role_required('entrepreneur')
def generatepayrollcertificate(request ,idnomina,idcontrato):
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




""" 
para el optimo funcionamiento del views , es requerido que se borre el icono 1 
se cambie la configuracion de correos electronicos y se cree la plantilla 

icono 1 : [:5] - linea 145 
icono 2 : recipient_list - entre la linea 152 - 158
icono 3 :  success, message - linea 177

"""

@login_required
@role_required('entrepreneur')
def massive_mail(request):
    if request.method == 'POST':
        nomina = request.POST.get('nomina2', '')
        
        # Verificación de que el campo nomina no esté vacío y sea un número
        if not nomina:
            return JsonResponse({'error': 'El campo nomina no debe estar vacío.'}, status=400)
        
        if not nomina.isdigit():
            return JsonResponse({'error': 'El campo nomina debe ser un número.'}, status=400)
        
        try:
            compectos = Nomina.objects.filter(idnomina=int(nomina)).distinct('idcontrato')[:5]
        except (ObjectDoesNotExist, MultipleObjectsReturned) as e:
            return JsonResponse({'error': f'Error al obtener los datos de Nomina: {str(e)}'}, status=500)
        except Exception as e:
            return JsonResponse({'error': f'Error inesperado al obtener los datos de Nomina: {str(e)}'}, status=500)

        recipient_list = [
            'mikepruebas@yopmail.com', 
            'alt.ru-1lmzxan@yopmail.com', 
            'alt.ya-9v5lsgo@yopmail.com', 
            'alt.ya-9v5lsgo@ydsopmail.com',
            'alt.ya-9v5lsgo@ydsopmail.com'
        ]
        
        cont = 0
        error = 0
        use = 0
        error_messages = []
        
        for comp in compectos:            
            context = genera_comprobante(nomina, comp.idcontrato.idcontrato)

            html_string = render(request, './html/payrollcertificate.html', context).content.decode('utf-8')

            fecha_actual = datetime.now().strftime('%Y-%m-%d')

            pdf = BytesIO()
            pisa_status = pisa.CreatePDF(html_string, dest=pdf)
            pdf.seek(0)

            if pisa_status.err:
                return HttpResponse('Error al generar el PDF', status=400)
            
            nombre_archivo = f'Certificado_{context["cc"]}_{fecha_actual}.pdf'
            
            # Enviar el PDF por correo
            email_subject = 'Tu Comprobante de Nòmina'
            
            recipient_list = ['mikepruebas@yopmail.com']  # Lista de destinatarios

            attachment = {
                'filename': nombre_archivo,
                'content': pdf.getvalue(),
                'mimetype': 'application/pdf'
            }
            
            
            try:
                if use < len(recipient_list):
                    success, message = send_template_email3(
                        email_type='nomina1',  # Ajusta el tipo de correo según corresponda
                        context=context,
                        subject=email_subject,
                        recipient_list=recipient_list,
                        attachment=attachment
                    )
                    if success:
                        cont += 1
                    else:
                        error += 1
                        error_messages.append(str(message))
                    use += 1
                else:
                    error_messages.append('Número insuficiente de destinatarios en recipient_list.')
            except Exception as e:
                error += 1
                error_messages.append(f'Error al enviar el correo: {str(e)}')

        response_data = {
            'correos_enviados': cont,
            'errores': error,
            'use': use,
            'mensajes_error': error_messages
        }
        
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Este view solo acepta peticiones POST.'}, status=405)



@login_required
@role_required('entrepreneur')
def unique_mail(request,idnomina,idcontrato):
    datacn = NominaComprobantes.objects.get(idnomina = idnomina ,idcontrato = idcontrato )
    context = genera_comprobante(idnomina, idcontrato)

    html_string = render(request, './html/payrollcertificate.html', context).content.decode('utf-8')

    fecha_actual = datetime.now().strftime('%Y-%m-%d')

    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=pdf)
    pdf.seek(0)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=400)
    nombre_archivo = f'Certificado_{context["cc"]}_{fecha_actual}.pdf'
    # Enviar el PDF por correo
    email_subject = 'Tu Comprobante de Nòmina'
    
    #
    recipient_list = ['mikepruebas@yopmail.com', context["mail"]]  # Lista de destinatarios

    attachment = {
        'filename': nombre_archivo,
        'content': pdf.getvalue(),
        'mimetype': 'application/pdf'
    }

    email_sent = send_template_email3(
        email_type='nomina1',  # Ajusta el tipo de correo según corresponda
        context=context,
        subject=email_subject,
        recipient_list=recipient_list,
        attachment=attachment
    )

    email_status = 'Correo enviado exitosamente.' if email_sent else 'Error al enviar el correo.'
    if email_sent :
        datacn.envio_email = 1
        datacn.save()
    else:
        datacn.envio_email = 2
        datacn.save()
        

    response_data = {
        'message': 'ID recibido correctamente',
        'status' : email_status,
        'name' : context["nombre_completo"]
    }
    return JsonResponse(response_data)





"""     
from django.shortcuts import render
from apps.companies.models import Nomina
from apps.components.humani import format_value




def payrollsheet(request):
    nominas = Nomina.objects.select_related('idnomina').values_list('idnomina__nombrenomina', 'idnomina').distinct().order_by('-idnomina')
    compects = []  # Define compects here
    acumulados = {}
    
    selected_nomina = request.GET.get('nomina')
    if selected_nomina:
        compectos = Nomina.objects.filter(idnomina = selected_nomina )
        
        

        
        
        
        for data in compectos:
            docidentidad = data.idempleado.docidentidad
            
            if docidentidad not in acumulados:
                
                acumulados[docidentidad] = {
                    'documento': docidentidad,
                    'nombre': f"{data.idempleado.papellido} {data.idempleado.sapellido} {data.idempleado.pnombre} {data.idempleado.snombre}",
                    'neto': data.valor,
                    'ingresos':data.valor if data.valor > 0 else 0 ,
                    'basico': data.valor if data.idconcepto.sueldobasico == 1 else 0 ,
                    'tpte': data.valor if data.idconcepto.auxtransporte == 1 else 0 ,
                    'extras': data.valor if data.idconcepto.extras == 1 else 0 ,
                    'aportess':data.valor if data.idconcepto.aportess == 1 else 0 ,
                    'prestamos': data.valor if data.idconcepto.idconcepto == 50 else 0 ,
                }
            else:
                acumulados[docidentidad]['neto'] += data.valor
                
                # Sumar el valor al campo ingresos si la condición se cumple
                if data.valor  > 0 :
                    print("anterir:",acumulados[docidentidad]['ingresos'],"Datos:", data, "Valor:", data.valor)
                    acumulados[docidentidad]['ingresos'] += data.valor
                    

                    
                
                # Sumar el valor al campo basico si la condición se cumple
                if data.idconcepto.sueldobasico == 1:
                    acumulados[docidentidad]['basico'] += data.valor
                
                
                # Sumar el valor al campo tpte si la condición se cumple
                if data.idconcepto.auxtransporte == 1:
                    acumulados[docidentidad]['tpte'] += data.valor
                
                
                # Sumar el valor al campo extras si la condición se cumple
                if data.idconcepto.extras == 1:
                    acumulados[docidentidad]['extras'] += data.valor
                    
                    
                # Sumar el valor al campo extras si la condición se cumple
                if data.idconcepto.aportess == 1:
                    acumulados[docidentidad]['aportess'] += data.valor
                    
                # Sumar el valor al campo extras si la condición se cumple
                if data.idconcepto.idconcepto == 50:
                    acumulados[docidentidad]['prestamos'] += data.valor
                    
        # Convertir el diccionario acumulado en una lista de diccionarios
        compects = list(acumulados.values())
    
    
    
    for compect in compects:
        # descuentos = neto - ingresos
        compect['descuentos'] = compect['neto'] - compect['ingresos']
        # otrosing = ingresos - basico - extras - transporte
        compect['otrosing'] = compect['ingresos'] - compect['basico'] - compect['extras'] - compect['tpte']
        # descuentos - prestamos - aportes
        compect['otrosdesc'] = compect['descuentos'] - compect['prestamos'] - compect['aportess']
    
    
    for compect in compects:
        compect['neto'] = format_value(compect['neto'])
        compect['ingresos'] = format_value(compect['ingresos'])
        compect['basico'] = format_value(compect['basico'])
        compect['tpte'] = format_value(compect['tpte'])
        compect['extras'] = format_value(compect['extras'])
        compect['aportess'] = format_value(compect['aportess'])
        compect['prestamos'] = format_value(compect['prestamos'])
        compect['descuentos'] = format_value(compect['descuentos'])
        compect['otrosing'] = format_value(compect['otrosing'])
        compect['otrosdesc'] = format_value(compect['otrosdesc'])
    
    
    # No need for else here, compects will be an empty list if it's not a POST request
    
    return render(request, 'companies/payrollsheet.html', {
        'nominas': nominas,
        'compects': compects,
        'selected_nomina':selected_nomina,
    })
""" 