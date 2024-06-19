from django.shortcuts import render ,redirect
from apps.components.decorators import custom_permission
from apps.employees.forms.newpasswordform import CustomPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required





@login_required
@custom_permission('employees')
def newpassword_employees(request):
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) 
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
            return redirect('employees:user')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, './employees/newpassword.html',{'form':form})
    
    





