# from django.shortcuts import render,redirect
# from apps.administrator.forms.rolesForm import RolesForm
# from django.contrib import messages
# from apps.administrator.models import Roles




# def role_admin(request):
#     if request.method == 'POST':
#         form = RolesForm(request.POST)
#         if form.is_valid():

#             nombre = form.cleaned_data['nombre'].capitalize()

#             Roles.objects.create(
#                 role_key=form.cleaned_data['tipo'],
#                 role_label=nombre
#             )
                
#             messages.success(request, 'El Rol Fue creado Correctamente')
#             return redirect('admin:companies')
#     else:
#         form = RolesForm()
#         roles = Roles.objects.all()
        
        
#     return render(request, './admin/role.html',{
#         'form': form,
#         'roles':roles
        
#         })