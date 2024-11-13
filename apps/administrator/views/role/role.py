from django.shortcuts import render,redirect
from apps.administrator.forms.rolesForm import RolesForm
from django.contrib import messages
from apps.common.models import Role




def role_admin(request):
    if request.method == 'POST':
        form = RolesForm(request.POST)
        if form.is_valid():
            Role.objects.create(
                name=form.cleaned_data['nombre'],
                description = form.cleaned_data['descripcion']
            )
            messages.success(request, 'El Rol Fue creado Correctamente')
            return redirect('admin:role')
    else:
        form = RolesForm()
        roles = Role.objects.all()
        
        
    return render(request, './admin/role.html',{
        'form': form,
        'roles':roles
        
        })