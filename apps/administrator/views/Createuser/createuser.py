from django.shortcuts import render,redirect
from apps.administrator.forms.createuserForm import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from apps.login.models import Usuario , Empresa

from django.shortcuts import get_object_or_404

def toggle_user_active_status(request, user_id, activate=True):
    usuario = get_object_or_404(Usuario, id=user_id)
    print(activate)
    usuario.user.is_active = activate
    usuario.user.save()
    print(usuario.user.username)
    print(usuario.user.is_active)
    status_message = 'activado' if activate else 'desactivado'
    messages.success(request, f'El usuario ha sido {status_message} con éxito.')
    return redirect('admin:user')


def user_admin(request):
    users = Usuario.objects.all()
    
    return render(request, './admin/users.html' , {'users':users}) 



def usercreate_admin(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            is_staff = form.cleaned_data['is_staff']
            is_superuser = form.cleaned_data['is_superuser']
            is_active = form.cleaned_data['is_active']
            
            company = Empresa.objects.get(id=form.cleaned_data['company'])
            
            

            # Crear el usuario
            
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                is_staff=is_staff,
                is_superuser=is_superuser,
                is_active=is_active
            )
            
            user.save()
            
                    
            usuario = Usuario.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                company=company,
                permission=form.cleaned_data['permission'],
                id_empleado=0  
            )
            
            usuario.save()
            
            messages.success(request, 'El cargo ha sido añadido con éxito.')
            return redirect('admin:user')
            # Redirigir a alguna página de éxito o realizar otras acciones necesarias
            #
    else:
        form = UserCreationForm()
    return render(request, './admin/usercreate.html',{'form': form})

