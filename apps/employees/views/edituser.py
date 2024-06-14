from django.shortcuts import render 
from apps.components.decorators import custom_login_required ,custom_permission
from apps.employees.models import Contratosemp ,Ciudades
from apps.employees.forms.edit_employees_form import EditEmployeesForm 
import base64




# @custom_login_required
# @custom_permission('employees')
def user_employees(request):
    ide = request.session.get('idempleado', {})
    data = Contratosemp.objects.only('direccionempleado', 'telefonoempleado', 'ciudadresidencia','fotografiaempleado','celular').get(idempleado=ide)
    ciudadresidencia = Ciudades.objects.get(idciudad=data.ciudadresidencia) if data.ciudadresidencia else None
    # direccionempleado
    # telefono 
    # ciudadresidencia
    
    return render(request, './employees/user.html',
                    {
                        'data':data,
                        'ciudadresidencia':ciudadresidencia,
                    }
                    )
    
    
def edit_user_employees(request):
    
    ide = request.session.get('idempleado', {})
    data = Contratosemp.objects.only('direccionempleado', 'telefonoempleado', 'ciudadresidencia','celular').get(idempleado=ide)
    
    
    if request.method == 'POST':
        form = EditEmployeesForm(request.POST, request.FILES)
        if form.is_valid():
            
            # Verificar si se proporcionó una nueva imagen
            if 'profile_picture' in request.FILES:
                data.fotografiaempleado = request.FILES['profile_picture']
            
            # Actualizar otros campos del empleado si es necesario
            if form.cleaned_data['phone'] is not None:
                data.telefonoempleado = form.cleaned_data['phone']
            if form.cleaned_data['cell'] is not None:
                data.direccionempleado = form.cleaned_data['cell']
            if form.cleaned_data['city'] is not None:
                data.direccionempleado = form.cleaned_data['city']
            if form.cleaned_data['address'] is not None:
                data.direccionempleado = form.cleaned_data['address']
            
            data.save()
    else:
        # Pre-poblar el formulario con datos existentes
        initial_data = {
            'phone': data.telefonoempleado,
            'address': data.direccionempleado,
            'cell': data.celular,
            'city': data.ciudadresidencia,
        }
        
        form = EditEmployeesForm(initial=initial_data)
    
    return render(request, './employees/edit_user.html', {'form': form }
                )





