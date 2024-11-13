from django.shortcuts import render,redirect
from apps.administrator.forms.createuserForm import UserCreationForm
from django.contrib import messages
from apps.common.models import User,Empresa , Role


from django.shortcuts import get_object_or_404

def toggle_user_active_status(request, user_id, activate=True):
    usuario = get_object_or_404(User, id=user_id)
    usuario.user.is_active = activate
    usuario.user.save()
    status_message = 'activado' if activate else 'desactivado'
    messages.success(request, f'El usuario ha sido {status_message} con éxito.')
    return redirect('admin:user')


def user_admin(request):
    users = User.objects.all().order_by('-id')
    
    return render(request, './admin/users.html' , {'users':users}) 



def usercreate_admin(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Obtener datos del formulario
            cleaned_data = form.cleaned_data
            id_empresa = Empresa.objects.get(idempresa=cleaned_data['company'])
            rol = Role.objects.get(id = cleaned_data['permission'] )
            # Crear el usuario
            user = User.objects.create_user(
                first_name=cleaned_data['first_name'],
                last_name=cleaned_data['last_name'],
                email=cleaned_data['email'],
                password=cleaned_data['password1'],
                id_empresa=id_empresa,
                tipo_user=cleaned_data['role'],
                rol = rol,
                is_staff=cleaned_data['is_staff'],
                is_superuser=cleaned_data['is_superuser'],
                is_active=cleaned_data['is_active'],
            )

            messages.success(request, 'El Usuario ha sido añadido con éxito.')
            return redirect('admin:user')

    else:
        form = UserCreationForm()

    return render(request, 'admin/usercreate.html', {'form': form})
