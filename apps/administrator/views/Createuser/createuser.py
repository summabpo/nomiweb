from django.shortcuts import render,redirect
from apps.administrator.forms.createuserForm import UserCreationForm
from django.contrib import messages
from apps.common.models import User,Empresa , Role
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


def toggle_user_active_status(request, user_id, activate=True):
    usuario = get_object_or_404(User, id=user_id)
    usuario.is_active = activate
    usuario.save()
    status_message = 'activado' if activate else 'desactivado'
    messages.success(request, f'El usuario ha sido {status_message} con éxito.')
    return redirect('admin:user')


def user_admin(request):
    users = User.objects.all().order_by('-id')
    form = UserCreationForm()
    return render(request, './admin/users.html' , {'users':users,'form':form}) 


def usercreate_admin(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Procesar el formulario y crear el usuario
            cleaned_data = form.cleaned_data
            id_empresa = Empresa.objects.get(idempresa=cleaned_data['company']) if cleaned_data['company'] else None
            rol = Role.objects.get(id=cleaned_data['permission'])
            User.objects.create_user(
                first_name=cleaned_data['first_name'],
                last_name=cleaned_data['last_name'],
                email=cleaned_data['email'],
                password=cleaned_data['password1'],
                id_empresa = id_empresa if cleaned_data['company'] else None,
                tipo_user=cleaned_data['role'],
                rol=rol,
                is_staff=cleaned_data['is_staff'],
                is_superuser=cleaned_data['is_superuser'],
                is_active=cleaned_data['is_active'],
            )
            
            return JsonResponse({'status': 'success', 'message': 'Formulario guardado exitosamente'})
        else:
            # En caso de que el formulario no sea válido, mostrar los errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    print(request, f"Error en {field}: {error}")
    else:
        form = UserCreationForm()
    return render(request, './admin/usercreate.html', {'form': form})
