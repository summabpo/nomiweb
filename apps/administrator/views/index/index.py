from django.shortcuts import render,redirect
from apps.administrator.forms.createuserForm import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.

def index_admin(request):
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
            
            messages.success(request, 'El cargo ha sido añadido con éxito.')
            #return redirect('companies:charges')
            # Redirigir a alguna página de éxito o realizar otras acciones necesarias
            #
    else:
        form = UserCreationForm()
    return render(request, './admin/index.html',{'form': form})