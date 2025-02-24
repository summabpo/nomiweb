
from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Cargos,Empresa,Nivelesestructura , Contabgrupos
from apps.companies.forms.accountinggroupForm import accountinggroupForm
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse



@login_required
@role_required('company','accountant')
def accountinggroup(request): 
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    groups = Contabgrupos.objects.filter(id_empresa__idempresa = idempresa ).order_by('idgrupo')
    form = accountinggroupForm()
    return render(request, './companies/accountinggroup.html',
                    {
                        'groups':groups,
                        'form':form,
                    })
    
    
@login_required
@role_required('company','accountant')
def accountinggroup_modal(request): 
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    if request.method == 'POST':
        form = accountinggroupForm(request.POST)
        if form.is_valid():
            empresa = Empresa.objects.get(idempresa= idempresa )
            
            nuevogrupo = Contabgrupos(
                    grupo=form.cleaned_data['grupo'] ,
                    grupocontable =form.cleaned_data['grupocontable'] ,
                    id_empresa = empresa
                )
            nuevogrupo.save()
            return JsonResponse({'status': 'success', 'message': 'Grupo creado exitosamente'})
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
                    
    else:
        form = accountinggroupForm()             
    
    return render(request, './companies/partials/accountinggroupModal.html',
                    {
                        'form':form,
                    })
    