from django.shortcuts import render 
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required





@login_required
@role_required('accountant')
def index_payroll(request):
    # usuario = request.session.get('usuario', {})
    # request.session['empleado'] = datos_empleado2(usuario['idempleado'])
    
    
    return render(request, './payroll/index.html')
    
    





