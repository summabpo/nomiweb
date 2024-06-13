from django.shortcuts import render 
from apps.components.decorators import custom_login_required ,custom_permission
from apps.components.dataemployees import datos_empleado2






@custom_login_required
@custom_permission('employees')
def index_employees(request):
    usuario = request.session.get('usuario', {})
    request.session['idempleado'] = usuario['id']

    request.session['empleado'] = datos_empleado2(usuario['id'])
    
    
    return render(request, './employees/index.html')
    
    





