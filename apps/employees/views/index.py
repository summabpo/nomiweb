from django.shortcuts import render 
from apps.components.dataemployees import datos_empleado2
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required





@login_required
@role_required('employee')
def index_employees(request):
    usuario = request.session.get('usuario', {})
    request.session['empleado'] = datos_empleado2(usuario['idempleado'])
    
    
    return render(request, './employees/index.html')
    
    





