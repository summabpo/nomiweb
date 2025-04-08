from django.shortcuts import render
from apps.common.models  import Liquidacion
from io import BytesIO
from xhtml2pdf import pisa
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
from apps.components.settlementgenerator import settlementgenerator
from apps.components.humani import format_value

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('company','accountant')
def settlementlist(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    liquidaciones = Liquidacion.objects.filter(idcontrato__id_empresa = idempresa ).order_by('idliquidacion')
    
    
    for compect in liquidaciones:
        # Accede a los atributos del modelo usando la notación de punto
        compect.cesantias = format_value(compect.cesantias)
        compect.intereses = format_value(compect.intereses)
        compect.prima = format_value(compect.prima)
        compect.vacaciones = format_value(compect.vacaciones)
        compect.totalliq = format_value(compect.totalliq)
    
    return render(request, 'companies/settlementlist.html',{
        'liquidaciones':liquidaciones,
    } )

@login_required
@role_required('company','accountant')
def settlementlistdownload(request,idliqui):
    
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    context = settlementgenerator(idliqui,idempresa)

    html_string = render(request, './html/liquidacion.html', context).content.decode('utf-8')
    
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