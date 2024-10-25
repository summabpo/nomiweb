from django.shortcuts import render, redirect, get_object_or_404
from apps.common.models  import Cargos,Empresa,Nivelesestructura
from apps.components.decorators import custom_login_required ,custom_permission
from apps.companies.forms.chargesForm import ChargesForm
from django.contrib import messages
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required

@login_required
@role_required('company')
def charges(request): 
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    if request.method == 'POST':
        form = form = ChargesForm(request.POST)
        if form.is_valid():
            empresa = Empresa.objects.get(idempresa = idempresa)
            nivel = Nivelesestructura.get( idnivel = form.cleaned_data['nombrecargo'] )
            nuevo_cargo = Cargos(
                nombrecargo=form.cleaned_data['nombrecargo'] ,
                nombrenivel = nivel,
                id_empresa = empresa
            )
            nuevo_cargo.save()
            messages.success(request, 'El cargo ha sido añadido con éxito.')
            return redirect('companies:charges')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en el campo '{field}': {error}")
    else:
        cargos = Cargos.objects.filter(id_empresa__idempresa=usuario['idempresa']).exclude(idcargo=93).order_by('idcargo')

        form = ChargesForm()
    
    return render(request, './companies/charges.html',
                    {
                        'cargos':cargos,
                        'form':form,
                    })
