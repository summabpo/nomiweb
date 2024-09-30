
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from apps.companies.models import  Nomina, Contratos, Conceptosfijos , Salariominimoanual
from apps.components.humani import format_value
from django.http import HttpResponse 
from .generate_docu import generate_nomina_excel

@login_required
@role_required('entrepreneur')
def externalreport(request):
    nominas ={}
    form = FilterForm()
    if request.method == 'POST':
        visual = True
        form = FilterForm(request.POST)
        if form.is_valid():
            año = form.cleaned_data['año']
            mes = form.cleaned_data['mes']
            year = año
            mth = mes
            nominas = Nomina.objects.filter(mesacumular=mes, anoacumular=año)\
                .select_related('idcontrato', 'idconcepto', 'idempleado', 'idcosto')\
                .values(
                    'idcontrato__idcontrato',
                    'idconcepto__cuentacontable',
                    'idempleado__docidentidad',
                    'idconcepto__idconcepto',
                    'idconcepto__nombreconcepto',
                    'valor',
                    'idcosto__idcosto'
                ).order_by('idcontrato__idcontrato')
                
            for item in nominas:
                item['valor'] = format_value(item['valor'])
            
    else :
        visual = False
        year = 0
        mth = 0

    
    return render (request, './companies/externalreport.html',
                    {
                        'visual':visual,
                        'nominas':nominas,
                        'year' : year,
                        'mth' : mth,
                        'form':form,
                    })
    
    
@login_required
@role_required('entrepreneur')
def download_excel_report(request):
    year = request.GET.get('year')
    month = request.GET.get('mth')

    # Verificar si year y month están presentes
    if not year or not month:
        return HttpResponse("Faltan parámetros.", status=400)

    # Generar el archivo Excel
    excel_data = generate_nomina_excel(year, month)
    file_name = f"informe_tercero_{month}_{year}.xlsx"
    
    # Crear la respuesta con el archivo Excel
    response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response

    
    
    