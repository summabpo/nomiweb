from django.shortcuts import render ,redirect
from apps.common.models import Contratosemp ,Ciudades
from apps.components.dataemployees import datos_empleado2
from apps.employees.forms.edit_employees_form import EditEmployeesForm 
from django.contrib import messages

from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required



@login_required
@role_required('employee')
def user_employees(request):
    usuario = request.session.get('usuario', {})
    ide = usuario['idempleado']
    data = Contratosemp.objects.only('direccionempleado', 'telefonoempleado', 'ciudadresidencia','fotografiaempleado','celular').get(idempleado=ide)
    
    # direccionempleado
    # telefono 
    # ciudadresidencia
    
    return render(request, './employees/user.html',
                    {
                        'data':data,
                    }
                    )
    
@login_required
@role_required('employee')   
def edit_user_employees(request):
    usuario = request.session.get('usuario', {})
    ide = usuario['idempleado']
    data = Contratosemp.objects.only('direccionempleado', 'telefonoempleado', 'ciudadresidencia','celular').get(idempleado=ide)
    
    
    if request.method == 'POST':
        
        form = EditEmployeesForm(request.POST, request.FILES)
        
        if 'profile_picture' in request.FILES:
            data.fotografiaempleado = request.FILES['profile_picture']
            data.save()
            request.session['empleado'] = datos_empleado2(usuario['id'])
            return redirect('employees:user')
        
        
        
        if form.is_valid():            
            # Verificar si se proporcionó una nueva imagen
            if 'profile_picture' in request.FILES:
                data.fotografiaempleado = request.FILES['profile_picture']            
            # Actualizar otros campos del empleado
            data.telefonoempleado = form.cleaned_data['phone'] or data.telefonoempleado
            data.celular = form.cleaned_data['cell'] or data.celular
            data.ciudadresidencia = Ciudades.objects.get(idciudad=form.cleaned_data['city']) if form.cleaned_data['city'] else data.ciudadresidencia
            data.direccionempleado = form.cleaned_data['address'] or data.direccionempleado

            data.save()
            request.session['empleado'] = datos_empleado2(ide)
            messages.success(request, '¡Éxito! Tus datos han sido actualizados correctamente')
            return redirect('employees:user')
        else:
            messages.error(request, 'Ha ocurrido un error inesperado. Por favor, intente nuevamente más tarde.')
    else:
        # Pre-poblar el formulario con datos existentes
        initial_data = {
            'phone': data.telefonoempleado,
            'address': data.direccionempleado,
            'cell': data.celular,
            'city': data.ciudadresidencia.idciudad,
        }
        
        form = EditEmployeesForm(initial=initial_data)
    
    return render(request, './employees/edit_user.html', {'form': form }
                )





