from django.shortcuts import render, redirect
from apps.companies.forms.EmployeeForm import EmployeeForm
from django.contrib import messages
from apps.common.models  import Contratosemp
from apps.companies.forms.EmployeeForm import EmployeeForm
from apps.companies.forms.ContractForm  import ContractForm 
from apps.common.models import User


from django.contrib.auth.hashers import make_password
from apps.components.mail import send_template_email

import random
import string
from apps.components.decorators import  role_required
from django.contrib.auth.decorators import login_required


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_password = ''.join(random.choice(characters) for i in range(length))
    return random_password

def hiring(request):
    usuario = request.session.get('usuario', {})
    idempresa = usuario['idempresa']
    
    empleados = [
        {
            'docidentidad': '123456789',
            'papellido': 'González',
            'sapellido': 'Martínez',
            'pnombre': 'Juan',
            'snombre': 'Carlos',
            'idempleado': 1
        },
        {
            'docidentidad': '987654321',
            'papellido': 'Pérez',
            'sapellido': 'Rodríguez',
            'pnombre': 'Ana',
            'snombre': 'María',
            'idempleado': 2
        },
        {
            'docidentidad': '456789123',
            'papellido': 'López',
            'sapellido': 'Fernández',
            'pnombre': 'Pedro',
            'snombre': 'José',
            'idempleado': 3
        },
        {
            'docidentidad': '321654987',
            'papellido': 'Ramírez',
            'sapellido': 'Torres',
            'pnombre': 'Marta',
            'snombre': 'Luisa',
            'idempleado': 4
        },
        {
            'docidentidad': '654987321',
            'papellido': 'Hernández',
            'sapellido': 'Gómez',
            'pnombre': 'Luis',
            'snombre': 'Alberto',
            'idempleado': 5
        }
    ]

    form_empleados = EmployeeForm() 
    form_contratos = ContractForm(idempresa=idempresa)
    return render(request, './companies/newContractVisual.html',{'empleados':empleados,'form_empleados':form_empleados , 'form_contratos':form_contratos})

@login_required
@role_required('company')
def newEmployee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            
            singleton = NombreDBSingleton()
            nombre_db = singleton.get_nombre_db()
            empresa = Empresa.objects.using('default').get(db_name=nombre_db)
            
            passwordoriginal = generate_random_password()
            password = make_password(passwordoriginal)
            
            
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
                'nombre_usuario': contratosemp_instance.pnombre,
                'usuario': contratosemp_instance.email,
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
        form = EmployeeForm()    
    return render(request, './companies/NewEmployee.html',{'form':form})
