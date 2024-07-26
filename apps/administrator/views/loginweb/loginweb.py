from django.shortcuts import render, redirect
from django.contrib import messages
from apps.companies.models import Contratos, Contratosemp
from apps.components.mail import send_template_email
from apps.login.models import Usuario, Empresa
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from apps.login.models import Empresa
import random
import string

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def create_user_and_usuario(email, pnombre, papellido, password, empresa, id_empleado):
    try:
        user = User.objects.create(
            username=email,
            first_name=pnombre,
            last_name=papellido,
            email=email,
            password=password,
            is_staff=False,
            is_superuser=False,
            is_active=True
        )
        user.save()
        usuario = Usuario.objects.create(
            user=user,
            role='employees',
            company=empresa,
            permission='none',
            id_empleado=id_empleado
        )
        usuario.save()
        
        return True, user, usuario
    except Exception as e:
        return False, None, None


def loginweb_admin(request,empresa='default'):
    
    if request.method == 'POST':
        
        selected_ids = request.POST.getlist('selected_ids')
        
        if selected_ids:
            for selected in selected_ids:
                print(selected)
                try:
                    usertempo = Contratosemp.objects.using(empresa).get(idempleado = int(selected))
                    usuario = Usuario.objects.get(id_empleado = int(selected))
                except Contratosemp.DoesNotExist:
                    messages.error(request, "No se encontró el empleado con ID seleccionado.")
                    return redirect('admin:loginweb',empresa=empresa)
                except Usuario.DoesNotExist:
                    usuario = None

                passwordoriginal = generate_random_password()
                password = make_password(passwordoriginal)
                
                if usuario:
                    usuario.user.password = password
                    usuario.user.save()
                else:
                    try:
                        empresa = Empresa.objects.get(db_name=empresa)
                        success, user, usuario = create_user_and_usuario(usertempo.email, usertempo.pnombre, usertempo.papellido, password, empresa, usertempo.idempleado)
                        if not success:
                            raise Exception("Error al crear el usuario.")
                    except Empresa.DoesNotExist:
                        messages.error(request, "No se encontró la empresa.")
                        return redirect('companies:loginweb')
                    except Exception as e:
                        messages.error(request, f"Error al crear el usuario: {e}")
                        pass

                email_type = 'loginweb'
                context = {
                    'nombre_usuario': usertempo.pnombre,
                    'usuario': usertempo.email,
                    'contrasena': passwordoriginal,
                }
                subject = 'Activacion de Usuario'
                recipient_list = ['mikepruebas@yopmail.com']

                if send_template_email(email_type, context, subject, recipient_list):
                    messages.success(request, 'El usuario ha sido creado con exito')
                    return redirect('admin:loginweb',empresa=empresa)
                else:
                    messages.error(request, 'Todo lo que podria salir mal, salio mal')

                messages.success(request, 'Los usuarios han sido enviados correctamente.')
                return redirect('companies:loginweb')





    contratos_empleados = Contratos.objects\
        .using(empresa)\
        .select_related('idempleado', 'idcosto', 'tipocontrato', 'idsede') \
        .filter(estadocontrato=1) \
        .values('idempleado__docidentidad', 'idempleado__papellido', 'idempleado__pnombre',
                'idempleado__snombre', 'cargo', 'idempleado__idempleado',
                'tipocontrato__tipocontrato','idempleado__email')

    empleados = []
    for contrato in contratos_empleados:
        nombre_empleado = f"{contrato['idempleado__papellido']} {contrato['idempleado__pnombre']} {contrato['idempleado__snombre']}"
        contrato_data = {
            'documento': contrato['idempleado__docidentidad'],
            'nombre': nombre_empleado,
            'cargo': contrato['cargo'],
            'tipocontrato': contrato['tipocontrato__tipocontrato'],
            'idempleado': contrato['idempleado__idempleado'],
            'email' : contrato['idempleado__email'],
        }
        empleados.append(contrato_data)

    return render(request, './admin/loginweb.html', {'empleados': empleados , 'empresa': empresa})


def select_loginweb_admin(request):
    if request.method == 'POST':
        empresa = request.POST.get('empresa_select')
        return redirect('admin:loginweb', empresa)
        
    empresas = Empresa.objects.exclude(name='admin')
    return render(request, './admin/selectloginweb.html', {'empresas': empresas})



def edit_main(request, empresa):
    if request.method == 'POST':
        correo1 = request.POST.get('correo1')
        correo2 = request.POST.get('correo2')
        
        try:
            usertempo = Contratosemp.objects.using(empresa).get(email=correo2)
        except Contratosemp.DoesNotExist:
            messages.error(request, 'No se encontró empleado con el correo electrónico proporcionado.')
            return redirect('admin:loginweb', empresa=empresa)
        
        try:
            usuario = Usuario.objects.get(id_empleado=usertempo.idempleado)
        except Usuario.DoesNotExist:
            messages.error(request, 'No se encontró usuario con el ID de empleado proporcionado.')
            return redirect('admin:loginweb', empresa=empresa)
        
        if correo1 == correo2:
            messages.warning(request, 'El correo electrónico ingresado ya está registrado para este empleado.')
            return redirect('admin:loginweb', empresa=empresa)
        else:
            usertempo.email = correo1
            try:
                usertempo.save(using=empresa)
            except Exception as e:
                print(f"Error saving usertempo: {e}")
                messages.error(request, 'Error al actualizar el correo electrónico del empleado.')
                return redirect('admin:loginweb', empresa=empresa)
            
            usuario.user.username = correo1
            usuario.user.email = correo1
            try:
                usuario.user.save()
            except Exception as e:
                print(f"Error saving usuario.user: {e}")
                messages.error(request, 'Error al actualizar el correo electrónico del empleado.')
                return redirect('admin:loginweb', empresa=empresa)
            messages.success(request, 'Correo electrónico actualizado correctamente.')
            return redirect('admin:loginweb', empresa=empresa)


        
    
    

