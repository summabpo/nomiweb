from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.forms.AbstractConceptForm import AbstractConceptForm
from apps.common.models import Nomina
from apps.components.humani import format_value
from django.contrib import messages
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.db.models import Sum


@login_required
@role_required('company','accountant')
def abstractconcept(request):
    """
    Muestra los conceptos abstractos asociados a una empresa y permite filtrarlos
    por concepto, nómina, empleado, mes y año.

    Filtra los registros de la nómina (`Nomina`) de acuerdo con los filtros proporcionados
    en el formulario. Si los filtros son válidos, se obtienen los resultados y se muestran
    en la plantilla correspondiente.

    Parameters
    ----------
    request : HttpRequest
        Objeto de solicitud HTTP con los datos del formulario y la sesión del usuario autenticado.

    Returns
    -------
    HttpResponse
        Respuesta que renderiza la plantilla `'companies/abstractconcept.html'` con los resultados
        filtrados y el formulario.

    See Also
    --------
    AbstractConceptForm : Formulario utilizado para capturar los filtros de búsqueda.
    Nomina : Modelo de nómina que se filtra según los parámetros seleccionados.
    role_required : Decorador personalizado que restringe el acceso según el rol.
    login_required : Decorador de Django que exige autenticación del usuario.

    Notes
    -----
    El usuario debe estar autenticado y tener el rol `'company'` o `'accountant'` para acceder a esta vista.
    """
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']

    if request.method == 'POST':
        form = AbstractConceptForm(request.POST, idempresa=idempresa)
        if form.is_valid():
            # Obtener y limpiar los datos del formulario
            def clean_value(v):
                if v is None:
                    return None
                if isinstance(v, str) and v.strip().lower() == "no data":
                    return None
                return v.strip() if isinstance(v, str) else v

            sconcept = clean_value(form.cleaned_data.get('sconcept'))
            payroll = clean_value(form.cleaned_data.get('payroll'))
            employee = clean_value(form.cleaned_data.get('employee'))
            month = clean_value(form.cleaned_data.get('month'))
            year = clean_value(form.cleaned_data.get('year'))

            
            # Construir los filtros dinámicamente
            filters = {
                'idconcepto__codigo': sconcept,
                'idnomina__idnomina': int(payroll) if payroll else None,
                'idcontrato__idempleado__idempleado': employee,
                'idnomina__mesacumular': month,
                'idnomina__anoacumular__ano': year,
                'idcontrato__id_empresa__idempresa': idempresa,
            }

            # Eliminar filtros vacíos o con valores None
            filters = {k: v for k, v in filters.items() if v not in [None, '', 'no data']}

            
            
            # Filtrar los datos
            nominas = Nomina.objects.filter(**filters).order_by('-idnomina')
            nomina = nominas if nominas.exists() else None

            return render(request, 'companies/abstractconcept.html', {
                'liquidaciones': nominas,
                'form': form,
            })

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            return redirect('companies:abstractconcept')
    else:
        nomina = {}

    # Crear una instancia del formulario de filtro para enviar al template
    form = AbstractConceptForm(idempresa=idempresa)

    # Renderizar el template con los resultados filtrados y el formulario
    return render(request, 'companies/abstractconcept.html', {
        'liquidaciones': nomina,
        'form': form,
    })
