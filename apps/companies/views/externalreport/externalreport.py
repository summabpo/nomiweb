
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.components.filterform import FilterForm 
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from apps.common.models import  Nomina, Contratos, Conceptosfijos , Salariominimoanual
from apps.components.humani import format_value
from django.http import HttpResponse 
from .generate_docu import generate_nomina_excel

@login_required
@role_required('company')
def externalreport(request):
    """
    Vista para generar y mostrar un informe externo de nómina.

    Esta vista permite a los usuarios autenticados con el rol 'company' generar un informe de nómina 
    basado en los filtros de año y mes. Los datos de la nómina se extraen de la base de datos y se muestran 
    en un formulario de informe visual. También permite descargar el informe como un archivo Excel.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los datos del formulario de filtro (año, mes) y la solicitud para 
        generar el informe de nómina.
    
    Returns
    -------
    HttpResponse
        Devuelve una respuesta HTTP que muestra el informe de nómina en el formulario, o genera una descarga 
        del archivo Excel con los datos de la nómina si la solicitud lo requiere.
    
    See Also
    --------
    FilterForm : Formulario para filtrar las nóminas por año y mes.
    Nomina : Modelo que representa las nóminas generadas por la empresa.
    format_value : Función que formatea los valores de la nómina.
    generate_nomina_excel : Función para generar el informe de nómina en formato Excel.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol 'company' para acceder a esta vista.
    La vista también incluye la opción de descargar un informe de la nómina como un archivo Excel.
    """

    nominas ={}
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    form = FilterForm()
    if request.method == 'POST':
        visual = True
        form = FilterForm(request.POST)
        if form.is_valid():
            año = form.cleaned_data['año']
            mes = form.cleaned_data['mes']
            year = año
            mth = mes
            nominas = Nomina.objects.filter(idnomina__mesacumular=mes, idnomina__anoacumular__ano=año ,idnomina__id_empresa__idempresa = idempresa)\
                .select_related('idcontrato', 'idconcepto', 'idcosto')\
                .values(
                    'idcontrato__idcontrato',
                    'idconcepto__cuentacontable',
                    'idcontrato__idempleado__docidentidad',
                    'idconcepto__codigo',
                    'idconcepto__nombreconcepto',
                    'valor',
                    'idcontrato__idcosto__idcosto'
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
@role_required('company')
def download_excel_report(request):
    """
    Vista para descargar el informe de nómina en formato Excel.

    Esta vista permite a los usuarios autenticados con el rol 'company' descargar un informe de nómina 
    basado en los parámetros de año y mes. Si los parámetros no se proporcionan, se retorna un error 
    indicando que faltan los parámetros necesarios. El archivo generado contiene los datos de las nóminas 
    de la empresa en el período solicitado.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP que contiene los parámetros de año y mes para generar el archivo Excel.
    
    Returns
    -------
    HttpResponse
        Devuelve una respuesta HTTP con el archivo Excel generado para la nómina correspondiente al año y mes 
        especificados.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol 'company' para acceder a esta vista.
    Si los parámetros 'year' y 'mth' no están presentes, se retorna un error con código de estado 400.
    """

    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    year = request.GET.get('year')
    month = request.GET.get('mth')

    # Verificar si year y month están presentes
    if not year or not month:
        return HttpResponse("Faltan parámetros.", status=400)

    # Generar el archivo Excel
    excel_data = generate_nomina_excel(year, month,idempresa)
    file_name = f"informe_tercero_{month}_{year}.xlsx"
    
    # Crear la respuesta con el archivo Excel
    response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response

    
    
    
