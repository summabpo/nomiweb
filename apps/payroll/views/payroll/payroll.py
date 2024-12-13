from django.shortcuts import render 
from apps.components.dataemployees import datos_empleado2
from django.contrib.auth.decorators import login_required
from apps.components.decorators import  role_required
from apps.common.models import Crearnomina




# @login_required
# @role_required('employee')
def payroll(request):
    nominas = Crearnomina.objects.filter(estadonomina = True)
    # usuario = request.session.get('usuario', {})
    # request.session['empleado'] = datos_empleado2(usuario['idempleado'])
    
    
    return render(request, './payroll/payroll.html',{'nominas':nominas})
    
    





