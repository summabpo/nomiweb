from django.shortcuts import render, redirect, get_object_or_404
from apps.companies.forms.EmployeeForm import EmployeeForm
from django.contrib import messages
from apps.companies.models import Tipodocumento , Paises , Ciudades , Contratosemp,Profesiones
from apps.companies.forms.EmployeeForm import EmployeeForm
from apps.components.decorators import custom_login_required ,custom_permission
from apps.login.models import Usuario , Empresa
from django.contrib.auth.models import User

from django.contrib.auth.hashers import make_password
from apps.login.middlewares import NombreDBSingleton
from apps.components.mail import send_template_email

import random
import string

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_password = ''.join(random.choice(characters) for i in range(length))
    return random_password


@custom_login_required
@custom_permission('entrepreneur')
def newEmployee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            
            singleton = NombreDBSingleton()
            nombre_db = singleton.get_nombre_db()
            empresa = Empresa.objects.using('default').get(db_name=nombre_db)
            
            
            try:
                height = form.cleaned_data['height']
                weight = form.cleaned_data['weight']
                height = height.replace(',', '.') if ',' in height else height
                weight = weight.replace(',', '.') if ',' in weight else weight
                height = float(height)
                weight = float(weight)
                
                contratosemp_instance = Contratosemp(
                docidentidad=form.cleaned_data['identification_number'],
                tipodocident=form.cleaned_data['identification_type'],
                pnombre=form.cleaned_data['first_name'],
                snombre=form.cleaned_data['second_name'],
                papellido=form.cleaned_data['first_last_name'],
                sapellido=form.cleaned_data['second_last_name'],
                fechanac=form.cleaned_data['birthdate'],
                ciudadnacimiento=form.cleaned_data['birth_city'],
                telefonoempleado=form.cleaned_data['employee_phone'],
                direccionempleado=form.cleaned_data['residence_address'],
                sexo=form.cleaned_data['sex'],
                email=form.cleaned_data['email'],
                ciudadresidencia=form.cleaned_data['residence_city'],
                estadocivil=form.cleaned_data['marital_status'],
                paisnacimiento=form.cleaned_data['birth_country'],
                paisresidencia=form.cleaned_data['residence_country'],
                celular=form.cleaned_data['cell_phone'],
                profesion=form.cleaned_data['profession'],
                niveleducativo=form.cleaned_data['education_level'],
                gruposanguineo=form.cleaned_data['blood_group'],
                estatura=height,
                peso=weight,
                fechaexpedicion=form.cleaned_data['expedition_date'],
                ciudadexpedicion=form.cleaned_data['expedition_city'],
                dotpantalon=form.cleaned_data['pants_size'],
                dotcamisa=form.cleaned_data['shirt_size'],
                dotzapatos=form.cleaned_data['shoes_size'],
                estrato=form.cleaned_data['stratum'],
                numlibretamil=form.cleaned_data['military_id'],
                estadocontrato=4
            )
                contratosemp_instance.save()
            except Exception as e:
                # Manejar el error de creación del empleado 
                messages.error(request, f"Error al crear el empleado: {e}")
                return redirect('companies:newemployee')
            
            try:
                singleton.set_nombre_db('default')
                password = make_password('prueba1')
                # Crea el usuario de Django
                user = User.objects.create(
                    username=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['first_last_name'],
                    email=form.cleaned_data['email'],
                    password=password,
                    is_staff=False,
                    is_superuser=False,
                    is_active=True
                )
                singleton.set_nombre_db(nombre_db)
            except Exception as e:
                # Manejar el error de creación de usuario
                messages.error(request, f"Error al crear el usuario: {e}")
                return redirect('companies:newemployee')
            
            
            try:
                singleton.set_nombre_db('default')
                empleado = contratosemp_instance.idempleado
                usuario = Usuario.objects.create(
                    user=user,
                    role='employees',
                    company=empresa, 
                    permission='none',
                    id_empleado = empleado
                )
                singleton.set_nombre_db(nombre_db)
            except Exception as e:
                # Manejar el error de creación de usuario
                messages.error(request, f"Error al crear los permisos : {e}")
                return redirect('companies:newemployee')
            
            
            email_type = 'loginweb'
            context = {
                'nombre_usuario': usertempo.pnombre,
                'usuario': usertempo.email,
                'contrasena': passwordoriginal,
            }
            subject = 'Activacion de Usuario'
            recipient_list = ['mikepruebas@yopmail.com'] ## cambiar el correo por el del usuario 
            #recipient_list = usertempo.email 

            if send_template_email(email_type, context, subject, recipient_list):
                pass
            else:
                messages.error(request, 'Todo lo que podria salir mal, salio mal')
                    
            messages.success(request, 'El Empleado ha sido creado')
            return  redirect('companies:newemployee')
    else:
        form = EmployeeForm    
    return render(request, './companies/NewEmployee.html',{'form':form})
