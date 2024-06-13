from django.shortcuts import render 
from apps.components.decorators import custom_login_required ,custom_permission
from apps.employees.models import Contratosemp ,Ciudades
from apps.employees.forms.edit_employees_form import EditEmployeesForm





# @custom_login_required
# @custom_permission('employees')
def user_employees(request):
    ide = request.session.get('idempleado', {})
    data = Contratosemp.objects.only('direccionempleado', 'telefonoempleado', 'ciudadresidencia','direccionempleado').get(idempleado=ide)
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
    form = EditEmployeesForm()
    
    return render(request, './employees/edit_user.html', {'form': form }
                )





