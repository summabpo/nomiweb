from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import threading
import time

#* tablas comunes 
class Anos(models.Model):
    idano = models.AutoField(primary_key=True) 
    ano = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return str(self.ano)

    class Meta:
        db_table = 'anos'
        
class Ausencias(models.Model):
    idausencia = models.AutoField(primary_key=True)  #int 
    ausencia = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.ausencia

    class Meta:
        db_table = 'ausencias'


class Profesiones(models.Model):
    idprofesion = models.AutoField(primary_key=True) 
    profesion = models.CharField(max_length=180, blank=True, null=True)
    
    def __str__(self):
        return self.profesion

    class Meta:
        db_table = 'profesiones'


class Nivelesestructura(models.Model):
    idnivel = models.AutoField(primary_key=True) 
    nombrenivel = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.nombrenivel

    class Meta:
        db_table = 'nivelesestructura'
        

class Cargos(models.Model):
    """
    tabla De cargos 
    
    requiere relacion de empresa 
    requiere validacion de nombrenivel 
    
    """
    idcargo = models.AutoField(primary_key=True)#models.AutoField(primary_key=True)
    nombrecargo = models.CharField(max_length=50)
    nombrenivel = models.ForeignKey(Nivelesestructura, on_delete=models.DO_NOTHING )
    estado = models.BooleanField(default=True)# por defecto true 
    id_empresa = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return  f"{self.nombrecargo} - {self.id_empresa}"

    class Meta:
        db_table = 'cargos'

class Costos(models.Model):
    """
    tabla Costos 
    idempresa 
    usar donde requiera 
    """
    idcosto = models.AutoField(primary_key=True) #models.AutoField(primary_key=True) 
    nomcosto = models.CharField(max_length=30, blank=True, null=True) 
    grupocontable = models.CharField(max_length=4, blank=True, null=True)
    suficosto = models.CharField(max_length=2, blank=True, null=True)
    id_empresa = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return  f"{self.nomcosto} - {self.id_empresa}"

    class Meta:
        db_table = 'costos'       

class Subcostos(models.Model):
    #igual 
    idsubcosto = models.AutoField(primary_key=True)
    nomsubcosto = models.CharField(max_length=30, blank=True, null=True)
    idcosto = models.ForeignKey(Costos, models.DO_NOTHING, blank=True, null=True)
    sufisubcosto = models.CharField(max_length=2, blank=True, null=True) 
    id_empresa = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return f"{self.nomsubcosto} - {self.id_empresa}"

    class Meta:
        db_table = 'subcostos' 


class Sedes(models.Model):
    idsede = models.AutoField(primary_key=True)
    nombresede = models.CharField(max_length=40, blank=True, null=True)
    cajacompensacion = models.CharField(max_length=60, blank=True, null=True)
    codccf = models.CharField(max_length=8, blank=True, null=True)
    id_empresa = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return  f"{self.nombresede} - {self.id_empresa}"

    class Meta:
        db_table = 'sedes'

class Conceptosfijos(models.Model):
    """
    tabla de Conceptosfijos
    Usarla donde deberia 
    """
    idfijo = models.AutoField(primary_key=True)
    conceptofijo = models.CharField(max_length=80, blank=True, null=True)
    valorfijo = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    
    def __str__(self):
        return self.conceptofijo
    
    class Meta:
        db_table = 'conceptosfijos'

class Subtipocotizantes(models.Model):
    """ 
    igual 
    """
    subtipocotizante = models.CharField(primary_key=True, max_length=2)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    codplanilla = models.SmallIntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.descripcion
    
    class Meta:
        db_table = 'subtipocotizantes'

class Paises(models.Model):
    idpais = models.AutoField(primary_key=True)
    pais = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.pais
    
    class Meta:
        db_table = 'paises'
        

class ModelosContratos(models.Model):
    """
    dejar quieta 
    """
    idmodelo = models.AutoField(primary_key=True)
    nombremodelo = models.CharField(max_length=255, blank=True, null=True)
    tipocontrato = models.CharField(max_length=255, blank=True, null=True)
    textocontrato = models.CharField(max_length=10485760, blank=True, null=True)
    estadomodelo = models.SmallIntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.nombremodelo
    
    class Meta:
        db_table = 'modelos_contratos'

class Ciudades(models.Model):
    idciudad = models.AutoField(primary_key=True)
    ciudad = models.CharField(max_length=50)
    departamento = models.CharField(max_length=50)
    codciudad = models.CharField(max_length=10)
    coddepartamento = models.CharField(max_length=10)
    
    def __str__(self):
        return self.ciudad
    
    class Meta:
        db_table = 'ciudades'

class Entidadessegsocial(models.Model):
    identidad = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=9)
    nit = models.CharField(max_length=12)
    entidad = models.CharField(max_length=120)
    tipoentidad = models.CharField(max_length=20)
    codsgp = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.entidad

    class Meta:
        db_table = 'entidadessegsocial'
        
class Diagnosticosenfermedades(models.Model):
    iddiagnostico = models.AutoField(primary_key=True)
    coddiagnostico = models.CharField(max_length=255)
    diagnostico = models.CharField(max_length=255)
    prefijo = models.CharField(max_length=1)
    
    def __str__(self):
        return self.coddiagnostico
    
    class Meta:
        db_table = 'diagnosticosenfermedades'
        

class Bancos(models.Model):
    """
    enlace contratos y empresas 
    """
    idbanco = models.AutoField(primary_key=True) 
    nombanco = models.CharField(max_length=255, )
    codbanco = models.CharField(max_length=255, )
    codach = models.CharField(max_length=255, blank=True, null=True)
    digchequeo = models.CharField(max_length=255)
    nitbanco = models.CharField(max_length=255, blank=True, null=True)
    tamcorriente = models.CharField(max_length=255)
    tamahorro = models.CharField(max_length=255)
    oficina = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.nombanco
    
    class Meta:
        db_table = 'bancos'


class Tipoavacaus(models.Model):
    idvac = models.AutoField(primary_key=True)
    nombrevacaus = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.nombrevacaus
    
    class Meta:
        db_table = 'tipoavacaus'


class Tipocontrato(models.Model):
    idtipocontrato = models.AutoField(primary_key=True)
    tipocontrato = models.CharField(max_length=255, blank=True, null=True)
    cod_dian = models.SmallIntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.tipocontrato
    
    class Meta:
        db_table = 'tipocontrato'


class Tipodenomina(models.Model):
    #igual 
    idtiponomina =models.AutoField(primary_key=True)
    tipodenomina = models.CharField(max_length=255)
    cod_dian = models.SmallIntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.tipodenomina
    
    class Meta:
        db_table = 'tipodenomina'


class Tipodocumento(models.Model):
    #igual 
    id_tipo_doc = models.AutoField(primary_key=True)
    documento = models.CharField(max_length=50, blank=True, null=True)
    codigo = models.CharField(max_length=4, blank=True, null=True)
    cod_dian = models.SmallIntegerField(blank=True, null=True)
    def __str__(self):
        return self.documento
    class Meta:
        db_table = 'tipodocumento'


class Tiposalario(models.Model):
    #igual 
    idtiposalario = models.AutoField(primary_key=True)
    tiposalario = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.tiposalario
    
    class Meta:
        db_table = 'tiposalario'


class Tiposdecotizantes(models.Model):
    #igual 
    tipocotizante = models.CharField(primary_key=True, max_length=2)
    descripcioncot = models.CharField(max_length=120, blank=True, null=True)
    codplanilla = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.tipocotizante

    class Meta:
        db_table = 'tiposdecotizantes'





class Centrotrabajo(models.Model):
    """
    tabla De Centros de trabajo 
    
    debe ser usada en contratos 
    """
    centrotrabajo = models.AutoField(primary_key=True)
    nombrecentrotrabajo = models.CharField(max_length=30)
    tarifaarl = models.DecimalField(max_digits=5, decimal_places=3)
    ctanterior = models.CharField(max_length=30,blank=True, null=True)
    id_empresa = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return  f"{self.nombrecentrotrabajo} - {self.id_empresa}"
    
    class Meta:
        db_table = 'centrotrabajo'


#* tablas espesificas - revisadas 

class Empresa(models.Model):
    idempresa = models.AutoField(primary_key=True)
    nit = models.CharField(max_length=20)
    nombreempresa = models.CharField(max_length=255)
    dv = models.CharField(max_length=10) 
    tipodoc = models.CharField(max_length=2)# Tipo de documento de empresa NI O CC o PP 
    # Representante legal
    replegal = models.CharField(max_length=255)

    # Datos de contacto principales
    direccionempresa = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20 )
    email = models.CharField(max_length=30 )
    codciudad = models.ForeignKey(Ciudades, on_delete=models.DO_NOTHING) 
    pais = models.ForeignKey(Paises, on_delete=models.DO_NOTHING)  
    
    # Detalles de ARL y códigos relacionados
    arl = models.ForeignKey(Entidadessegsocial, on_delete=models.DO_NOTHING  ,related_name='contratos_arl')#enlace -> Entidadessegsocial   

    # Detalles de nómina y RRHH 
    contactonomina = models.CharField(max_length=50)
    emailnomina = models.CharField(max_length=50)
    contactorrhh = models.CharField(max_length=50)
    emailrrhh = models.CharField(max_length=50)

    # Contabilidad y certificaciones 
    contactocontab = models.CharField(max_length=50)
    emailcontab = models.CharField(max_length=50)
    
    
    cargocertificaciones = models.CharField(max_length=50)
    firmacertificaciones = models.CharField(max_length=50)

    # Detalles adicionales
    website = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=40, blank=True, null=True)
    metodoextras = models.CharField(max_length=255, blank=True, null=True)
    # Campos relacionados con aportes y parafiscales
    realizarparafiscales = models.CharField(max_length=2, blank=True, null=True)
    vstccf = models.CharField(max_length=2, blank=True, null=True)
    vstsenaicbf = models.CharField(max_length=2, blank=True, null=True)
    ige100 = models.CharField(max_length=2, blank=True, null=True)
    slntarifapension = models.CharField(max_length=2, blank=True, null=True)

    # Detalles bancarios
    banco = models.ForeignKey(Bancos, on_delete=models.DO_NOTHING, blank=True, null=True ) # Posible enlace -> banco 
    numcuenta = models.CharField(max_length=255, blank=True, null=True)
    tipocuenta = models.CharField(max_length=10, blank=True, null=True)

    # Sucursales y aportantes #redundante y posible nueva tabla 
    codigosuc = models.CharField(max_length=10, blank=True, null=True)
    nombresuc = models.CharField(max_length=40, blank=True, null=True)
    claseaportante = models.CharField(max_length=1, blank=True, null=True)
    tipoaportante = models.SmallIntegerField(blank=True, null=True)
    
    ajustarnovedad = models.CharField(max_length=2, blank=True, null=True)
    
    def __str__(self):
        return self.nombreempresa
    
    class Meta:
        db_table = 'empresa'
        verbose_name = "empresa"
        verbose_name_plural = "empresas"



class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        db_table = 'role'


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(('El email es obligatorio'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    TIPO_USER_CHOICES = [
        ('admin', 'Administrator'),
        ('employee', 'Employee'),
        ('company', 'Company'),
        ('accountant', 'Accountant'),
    ]

    username = None
    email = models.EmailField(unique=True)
    tipo_user = models.CharField(max_length = 10, choices = TIPO_USER_CHOICES, default='admin')
    rol = models.ForeignKey(Role, on_delete = models.DO_NOTHING, null=True)
    id_empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, blank=True, null=True)
    id_empleado = models.ForeignKey('Contratosemp', on_delete=models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email}"

    def is_admin(self):
        return self.tipo_user == 'admin'

    def is_employee(self):
        return self.tipo_user == 'employee'
    
    def is_company(self):
        return self.tipo_user == 'company'
    
    
    def is_accountant(self):
        return self.tipo_user == 'accountant'
    
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        db_table = 'user'

class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE , blank=True, null=True)
    token_temporal = models.CharField(max_length=100 , blank=True, null=True)
    tiempo_creacion = models.DateTimeField(auto_now_add=True , blank=True, null=True)
    estado = models.BooleanField(default=True , blank=True, null=True )
    
    class Meta:
        db_table = 'token'
        verbose_name = "token"
        verbose_name_plural = "tokens"

@receiver(post_save, sender=Token)
def eliminar_objeto_despues_dos_horas(sender, instance, **kwargs):
    def cambiar_estado():
        time.sleep(120)
        instance.estado = False
        instance.save()

    threading.Thread(target=cambiar_estado).start()

class EditHistory(models.Model):
    modified_model = models.CharField(max_length=100)  # Nombre del modelo modificado
    modified_object_id = models.PositiveIntegerField()  # ID del objeto modificado
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Usuario que hizo la modificación
    modification_time = models.DateTimeField(default=timezone.now)  # Fecha de la modificación
    operation_type = models.CharField(max_length=10, choices=[  # Tipo de operación
        ('update', 'Actualización'),
        ('delete', 'Eliminación')
    ])
    field_name = models.CharField(max_length=100, blank=True, null=True)  
    old_value = models.TextField(blank=True, null=True)  # Valor anterior (si aplica)
    new_value = models.TextField(blank=True, null=True)  # Valor nuevo (si aplica)
    description = models.TextField()  # Descripción de la modificación 
    id_empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, blank=True, null=True)
    
    def __str__(self):
        return f"{self.modified_model} (ID: {self.modified_object_id}) modificado por {self.user} el {self.modification_time}"

    class Meta:
        verbose_name = 'Historial de modificación'
        verbose_name_plural = 'Historial de modificaciones'
        db_table = 'history'
        ordering = ['-modification_time'] 
        
        
class Contratosemp(models.Model):
    idempleado = models.AutoField(primary_key=True)
    docidentidad = models.BigIntegerField(unique=True)
    tipodocident = models.ForeignKey(Tipodocumento, on_delete=models.DO_NOTHING)

    # Nombres y apellidos
    pnombre = models.CharField(max_length=50)
    snombre = models.CharField(max_length=50,blank=True, null=True)
    papellido = models.CharField(max_length=50)
    sapellido = models.CharField(max_length=50,blank=True, null=True)

    # Información de contacto
    email = models.CharField(max_length=255, blank=True, null=True)
    telefonoempleado = models.CharField(max_length=12, blank=True, null=True)
    celular = models.CharField(max_length=12, blank=True, null=True)
    direccionempleado = models.CharField(max_length=100, blank=True, null=True)

    # Datos personales
    sexo = models.CharField(max_length=255, blank=True, null=True)
    fechanac = models.DateField()
    ciudadnacimiento = models.ForeignKey(Ciudades, on_delete=models.DO_NOTHING,related_name='ciudad_nacimiento')
    paisnacimiento = models.ForeignKey(Paises, on_delete=models.DO_NOTHING,related_name='pais_nacimiento')

    ciudadresidencia = models.ForeignKey(Ciudades, on_delete=models.DO_NOTHING,related_name='ciudad_recidencia' )
    paisresidencia = models.ForeignKey(Paises, on_delete=models.DO_NOTHING,related_name='pais_recidencia' )
    estadocivil = models.CharField(max_length=20, blank=True, null=True)

    # Datos académicos y profesionales
    profesion = models.CharField(max_length=180, blank=True, null=True)
    niveleducativo = models.CharField(max_length=25, blank=True, null=True)

    # Información física
    estatura = models.CharField(max_length=10, blank=True, null=True)
    peso = models.CharField(max_length=10, blank=True, null=True)
    gruposanguineo = models.CharField(max_length=10, blank=True, null=True)

    # Documentación
    fechaexpedicion = models.DateField(blank=True, null=True)
    ciudadexpedicion = models.ForeignKey(Ciudades, on_delete=models.DO_NOTHING,related_name='ciudad_expedicion')
    formatohv = models.CharField(max_length=25,blank=True, null=True)

    # Dotaciones
    dotpantalon = models.CharField(max_length=10, blank=True, null=True)
    dotcamisa = models.CharField(max_length=10, blank=True, null=True)
    dotzapatos = models.CharField(max_length=10, blank=True, null=True)

    # Otros datos
    estadocontrato = models.SmallIntegerField(blank=True, null=True)
    estrato = models.CharField(max_length=5, blank=True, null=True)
    numlibretamil = models.CharField(max_length=10, blank=True, null=True)

    # Fotografía
    fotografiaempleado = models.CharField(max_length=25,blank=True, null=True)

    # Relación con la empresa
    id_empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING )
    
    class Meta:
        db_table = 'contratosemp'


class Contratos(models.Model):
    """
    tabla de Contratos
    Usarla donde deberia 
    """
    """
    Choices
    Estadocontrato
    1 - activo
    2- retirado

    Estadoliquidacion
    3- activo
    2- retirado
    1 - en proceso liquidación

    Estadosegsocial
    3- activo
    2- retirado
    1 - en proceso por retirar de ss
    """
    idcontrato = models.AutoField(primary_key=True) 
    cargo = models.ForeignKey(Cargos, on_delete=models.DO_NOTHING) 
    fechainiciocontrato = models.DateField(blank=True, null=True)
    fechafincontrato = models.DateField(blank=True, null=True)
    tipocontrato = models.ForeignKey(Tipocontrato, on_delete=models.DO_NOTHING)
    tiponomina = models.ForeignKey(Tipodenomina, on_delete=models.DO_NOTHING)
    bancocuenta = models.ForeignKey(Bancos, on_delete=models.DO_NOTHING) 
    cuentanomina = models.CharField(max_length=30, blank=True, null=True) 
    tipocuentanomina = models.CharField(max_length=15, blank=True, null=True) # choice agreagar deposito electronico 
    centrotrabajo = models.ForeignKey(Centrotrabajo, on_delete=models.DO_NOTHING)
    ciudadcontratacion =models.ForeignKey(Ciudades, on_delete=models.DO_NOTHING) 
    estadocontrato = models.SmallIntegerField(blank=True, null=True)# choice de estados 
    salario = models.IntegerField(blank=True, null=True) 
    idempleado = models.ForeignKey(Contratosemp, models.DO_NOTHING, blank=True, null=True) 
    tipocotizante =  models.ForeignKey(Tiposdecotizantes, on_delete=models.DO_NOTHING)  
    subtipocotizante =  models.ForeignKey(Subtipocotizantes, on_delete=models.DO_NOTHING)  
    formapago = models.CharField(max_length=25, blank=True, null=True)#Choice 
    metodoretefuente = models.CharField(max_length=25, blank=True, null=True) #choice - formula o  calculo por año
    porcentajeretefuente = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) 
    valordeduciblevivienda = models.IntegerField(blank=True, null=True)
    saludretefuente = models.IntegerField(blank=True, null=True)
    pensionado = models.CharField(max_length=25, blank=True, null=True)
    estadoliquidacion = models.CharField(max_length=25,blank=True, null=True)#choice Estadoliquidacion  
    estadosegsocial = models.CharField(max_length=25,blank=True, null=True)#choice Estadosegsocial 
    motivoretiro = models.CharField(max_length=25, blank=True, null=True)#unificar con choice 
    tiposalario = models.ForeignKey(Tiposalario, models.DO_NOTHING, blank=True, null=True)#Posible choice
    
    idcosto = models.ForeignKey(Costos, models.DO_NOTHING, blank=True, null=True)
    idsubcosto = models.ForeignKey(Subcostos, models.DO_NOTHING, blank=True, null=True)
    idsede = models.ForeignKey(Sedes, models.DO_NOTHING, blank=True, null=True) 
    salariovariable = models.SmallIntegerField(blank=True, null=True,default=2)
    codeps = models.ForeignKey(Entidadessegsocial, on_delete=models.DO_NOTHING,related_name='contratos_eps'  ) 
    codafp = models.ForeignKey(Entidadessegsocial, on_delete=models.DO_NOTHING,related_name='contratos_afp'  ) 
    codccf = models.ForeignKey(Entidadessegsocial, on_delete=models.DO_NOTHING,related_name='contratos_ccf'  ) 
    fondocesantias = models.ForeignKey(Entidadessegsocial, on_delete=models.DO_NOTHING,related_name='contratos_fondocesantias' ,blank=True, null=True ) 
    auxiliotransporte = models.BooleanField(default=False)
    dependientes = models.SmallIntegerField(blank=True, null=True)#manualmente 
    valordeduciblemedicina = models.IntegerField(blank=True, null=True)#manualmente 
    jornada = models.CharField(max_length=25,blank=True, null=True)#choice
    idmodelo = models.ForeignKey(ModelosContratos, models.DO_NOTHING) #enlace modelos_contratos
    riesgo_pension = models.BooleanField(default=False)
    id_empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)
    
    class Meta:
        db_table = 'contratos'



class Ausentismo(models.Model):
    """
    Pendiente de validacion : uso 
    """
    idausentismo = models.AutoField(primary_key=True)
    ausencia = models.ForeignKey(Ausencias, on_delete=models.DO_NOTHING ) # id ausensia 
    remunerado = models.BooleanField(default=False) 
    horasdescontar = models.IntegerField(blank=True, null=True) 
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING)
    fechanovedad = models.DateField(blank=True, null=True)
    autorizadopor = models.CharField(max_length=50, blank=True, null=True) 
    horainicio = models.TimeField(blank=True, null=True)
    horafin = models.TimeField(blank=True, null=True)
    horasausencia = models.IntegerField(blank=True, null=True) # texto 
    estadoausentismo = models.SmallIntegerField(blank=True, null=True)# Cambio de tipo 
    idnomina = models.IntegerField(blank=True, null=True)#Posible enlace 

    class Meta:
        db_table = 'ausentismo'
        

## modelos normales 
"""
Posible cambio de nombre 
posible cambio de nombre - columnas 

"""







class Certificaciones(models.Model):
    """
    tabla De Certificaciones 
    """
    idcert = models.AutoField(primary_key=True)
    destino = models.CharField(max_length=100, blank=True, null=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING) 
    fecha = models.DateField(blank=True, null=True)
    salario = models.IntegerField()# fija requerido  
    cargo = models.ForeignKey(Cargos, on_delete=models.DO_NOTHING) # fija requerido 
    tipocontrato = models.CharField(max_length=30)# fija requerido 
    promediovariable = models.IntegerField(blank=True, null=True) # calculo  
    codigoconfirmacion = models.CharField(max_length=8, blank=False, null=False, unique=True)
    tipocertificacion = models.IntegerField(blank=True, null=True)
    

    class Meta:
        db_table = 'certificaciones'
        


class Cesantias(models.Model):
    idces = models.AutoField(primary_key=True) #models.AutoField(primary_key=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING) 
    valcesa = models.IntegerField(blank=True, null=True)
    valint = models.IntegerField(blank=True, null=True)
    anoacumular = models.ForeignKey(Anos, models.DO_NOTHING ) # enlace a años  
    salario = models.IntegerField(blank=True, null=True)
    transporte = models.IntegerField(blank=True, null=True)
    extras = models.IntegerField(blank=True, null=True)
    diascesa = models.IntegerField(blank=True, null=True)
    fondo = models.CharField(max_length=255, blank=True, null=True) # codigo fondo ces 
    valcesaacum = models.IntegerField(blank=True, null=True) # acomulado variable 
    diassuspension = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'cesantias'





class Conceptosdenomina(models.Model):
    idconcepto = models.AutoField(primary_key=True)
    nombreconcepto = models.CharField(max_length=30)
    multiplicadorconcepto = models.DecimalField(max_digits=4, decimal_places=2)
    tipoconcepto = models.IntegerField()
    sueldobasico =  models.BooleanField(default=False)
    auxtransporte =  models.BooleanField(default=False)
    baseprestacionsocial =  models.BooleanField(default=False)
    ingresotributario =  models.BooleanField(default=False)
    prestacionsocial =  models.BooleanField(default=False)
    extras =  models.BooleanField(default=False)
    basesegsocial =  models.BooleanField(default=False)
    cuentacontable = models.CharField(max_length=25, blank=True, null=True) #*
    ausencia =  models.BooleanField(default=False)
    salintegral =  models.BooleanField(default=False)
    basevacaciones =  models.BooleanField(default=False)
    formula = models.CharField(max_length=1, blank=True, null=True) #*
    basetransporte =  models.BooleanField(default=False)
    aportess =  models.BooleanField(default=False)
    incapacidad =  models.BooleanField(default=False)
    base1393 =  models.BooleanField(default=False)
    norenta =  models.BooleanField(default=False)
    pension =  models.BooleanField(default=False)
    exentos =  models.BooleanField(default=False)
    baserarl =  models.BooleanField(default=False)
    basecaja =  models.BooleanField(default=False)
    viaticos =  models.BooleanField(default=False)
    comisiones =  models.BooleanField(default=False)
    gastosderep =  models.BooleanField(default=False)
    suspcontrato =  models.BooleanField(default=False)
    grupo_dian = models.CharField(max_length=255, blank=True, null=True) #*
    id_empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)
    
    
    class Meta:
        db_table = 'conceptosdenomina'
    
    def __str__(self):
        return f"{self.nombreconcepto}"





class Contabcuentas(models.Model):
    """
    tabla de Contabcuentas
    Usarla donde deberia 
    Idempresa  
    quitar :idcuentacontable = 1 y idcuentacontable = 2 
    """
    idcuenta = models.AutoField(primary_key=True)
    idcuentacontable = models.CharField(max_length=12, blank=True, null=True)
    cuentacontable = models.CharField(max_length=50, blank=True, null=True)
    id_empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'contabcuentas'


class Contabgrupos(models.Model):
    idgrupo = models.AutoField(primary_key=True)
    grupo = models.CharField(max_length=2)
    grupocontable = models.CharField(max_length=40, blank=True, null=True)
    id_empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)
    
    class Meta:
        db_table = 'contabgrupos'


###! preguntar 
# class ContratosImportador(models.Model):
#     idcontrato = models.SmallIntegerField(primary_key=True)
#     novedad1 = models.CharField(max_length=255, blank=True, null=True)
#     novedad2 = models.CharField(max_length=255, blank=True, null=True)
#     novedad3 = models.CharField(max_length=255, blank=True, null=True)
#     novedad4 = models.CharField(max_length=255, blank=True, null=True)

#     class Meta:
#      
#         db_table = 'contratos_importador'



class Crearnomina(models.Model):
    """
    tabla Crearnomina 
    idempresa 
    usar donde requiera 
    """
    idnomina = models.AutoField(primary_key=True)#models.AutoField(primary_key=True) 
    nombrenomina = models.CharField(max_length=40, blank=True, null=True)## tipo ( liquidacion o nomina ) mes  - año = nomina - enero - 2024 - 1 o 2
    fechainicial = models.DateField(blank=True, null=True)
    fechafinal = models.DateField(blank=True, null=True)
    fechapago = models.DateField(blank=True, null=True)
    tiponomina = models.ForeignKey(Tipodenomina, on_delete=models.DO_NOTHING )  # enlace tipodenomina 
    mesacumular = models.CharField(max_length=20, blank=True, null=True) 
    anoacumular = models.ForeignKey(Anos, models.DO_NOTHING ) # año 
    estadonomina =models.BooleanField(default=False)
    diasnomina = models.SmallIntegerField(blank=True, null=True)
    id_empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING,null=True, blank=True)
    
    class Meta:
        db_table = 'crearnomina'





# class DocCategorias(models.Model):
#     """
#     se deja igual 
#     """
#     idcat = models.IntegerField(primary_key=True)
#     doc_categoria = models.CharField(max_length=100)

#     class Meta:
#      
#         db_table = 'doc_categorias'


# class DocDocumentos(models.Model):
#     """
#     se deja igual 
#     """
#     iddoc = models.IntegerField(primary_key=True)
#     tipo = models.CharField(blank=True, null=True)
#     titulo = models.CharField(blank=True, null=True)
#     idempleado = models.CharField(blank=True, null=True)
#     fecha = models.DateField(blank=True, null=True)
#     usuario = models.CharField(blank=True, null=True)
#     documento = models.BinaryField(blank=True, null=True)
#     nomarchivo = models.CharField(blank=True, null=True)
#     tamarchivo = models.CharField(blank=True, null=True)

#     class Meta:
#      
#         db_table = 'doc_documentos'


class EmpVacaciones(models.Model):
    """
    Tabla para gestionar las solicitudes de vacaciones de los empleados.
    """
    id_sol_vac = models.AutoField(primary_key=True)  
    idcontrato = models.ForeignKey('Contratos', on_delete=models.DO_NOTHING)  
    tipovac = models.ForeignKey('Tipoavacaus', on_delete=models.DO_NOTHING)  
    fechainicialvac = models.DateField(blank=True, null=True)  
    fechafinalvac = models.DateField(blank=True, null=True)  
    estado = models.SmallIntegerField(blank=True, null=True)  # Estado de la solicitud (0: pendiente, 1: aprobado, 2: rechazado, etc.)
    diasvac = models.SmallIntegerField(blank=True, null=True)  
    cuentasabados = models.BooleanField(default=False)  
    estadovac = models.SmallIntegerField()
    diascalendario = models.SmallIntegerField(blank=True, null=True)  
    ip_usuario = models.CharField(max_length=16, blank=True, null=True)  # Dirección IP del usuario que realiza la solicitud
    fecha_hora = models.DateTimeField(blank=True, null=True)  # Fecha y hora de la solicitud
    comentarios = models.CharField(max_length=255, blank=True, null=True)  # Comentarios adicionales
    comentarios2 = models.CharField(max_length=255, blank=True, null=True)  # Comentarios adicionales (opcional)

    class Meta:  
        db_table = 'emp_vacaciones'   



class EstActivos(models.Model):
    """
    se deja igual 
    """
    idmes = models.AutoField(primary_key=True)
    mes = models.CharField(max_length=255, blank=True, null=True)
    ano = models.IntegerField(blank=True, null=True)
    empleados = models.SmallIntegerField(blank=True, null=True)
    devengados = models.IntegerField(blank=True, null=True)
    extras = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'est_activos'




class Festivos(models.Model):
    """
    festivos : añadir automatizacion 
    """
    idfestivo = models.AutoField(primary_key=True)
    dia = models.DateField(blank=True, null=True)
    descripcion = models.CharField(max_length=60, blank=True, null=True)
    ano = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'festivos'


class Incapacidades(models.Model):
    """
    
    """
    idincapacidad = models.AutoField(primary_key=True)#models.AutoField(primary_key=True)
    certificadoincapacidad = models.CharField(max_length=15, blank=True, null=True)
    entidad = models.ForeignKey(Entidadessegsocial, on_delete=models.DO_NOTHING) #enlace segsocial
    coddiagnostico = models.ForeignKey(Diagnosticosenfermedades, on_delete=models.DO_NOTHING) 
    fechainicial = models.DateField(blank=True, null=True)
    dias = models.IntegerField(blank=True, null=True)
    imagenincapacidad = models.CharField(max_length=100 ,blank=True, null=True) # cambiar tipo enlace 
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING) 
    prorroga = models.BooleanField(default=False) #boleano 
    ibc = models.IntegerField(blank=True, null=True)# calculado 
    origenincap = models.CharField(max_length=100,blank=True, null=True) # choice 

    class Meta:
        db_table = 'incapacidades'



class IncapacidadesImportador(models.Model):
    
    """
    igual a Incapacidades mejora de incapacidades 
    """
    
    idincapacidad = models.AutoField(primary_key=True)#models.AutoField(primary_key=True)
    certificadoincapacidad = models.CharField(max_length=15, blank=True, null=True)
    entidad = models.ForeignKey(Entidadessegsocial, on_delete=models.DO_NOTHING) #enlace segsocial
    coddiagnostico = models.ForeignKey(Diagnosticosenfermedades, on_delete=models.DO_NOTHING) 
    fechainicial = models.DateField(blank=True, null=True)
    dias = models.IntegerField(blank=True, null=True)
    imagenincapacidad = models.CharField(max_length=100 ,blank=True, null=True) # cambiar tipo enlace 
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING) 
    prorroga = models.BooleanField(default=False) #boleano 
    ibc = models.IntegerField(blank=True, null=True)# calculado 
    origenincap = models.CharField(max_length=100,blank=True, null=True) # choice 
    
    class Meta:
        db_table = 'incapacidades_importador'


class Ingresosyretenciones(models.Model):
    idingret =models.AutoField(primary_key=True) #models.AutoField(primary_key=True)
    salarios = models.IntegerField(blank=True, null=True)
    honorarios = models.IntegerField(blank=True, null=True)
    servicios = models.IntegerField(blank=True, null=True)
    comisiones = models.IntegerField(blank=True, null=True)
    prestacionessociales = models.IntegerField(blank=True, null=True)
    viaticos = models.IntegerField(blank=True, null=True)
    gastosderepresentacion = models.IntegerField(blank=True, null=True)
    compensacioncta = models.IntegerField(blank=True, null=True)
    cesantiasintereses = models.IntegerField(blank=True, null=True)
    pensiones = models.IntegerField(blank=True, null=True)
    totalingresosbrutos = models.IntegerField(blank=True, null=True)
    aportessalud = models.IntegerField(blank=True, null=True)
    aportespension = models.IntegerField(blank=True, null=True)
    aportesvoluntarios = models.IntegerField(blank=True, null=True)
    aportesafc = models.IntegerField(blank=True, null=True)
    retefuente = models.IntegerField(blank=True, null=True)
    anoacumular = models.ForeignKey(Anos, models.DO_NOTHING)
    idempleado = models.ForeignKey('Contratosemp', models.DO_NOTHING) #enlace principal 
    otrospagos = models.IntegerField(blank=True, null=True)
    fondocesantias = models.IntegerField(blank=True, null=True)
    excesoalim = models.IntegerField(blank=True, null=True)
    cesantias90 = models.IntegerField(blank=True, null=True)
    apoyoeconomico = models.IntegerField(blank=True, null=True)
    aportesavc = models.IntegerField(blank=True, null=True)
    ingresolaboralpromedio = models.IntegerField(blank=True, null=True)
    id_empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'ingresosyretenciones'


# class Jornadas(models.Model):
#     """
#     dejar por ahora , posible analisis 
#     """
#     idjornada = models.SmallIntegerField()
#     jornada = models.CharField(max_length=40, blank=True, null=True)
#     extras = models.CharField(blank=True, null=True)
#     lunes1 = models.CharField(blank=True, null=True)
#     lunes2 = models.CharField(blank=True, null=True)
#     martes1 = models.CharField(blank=True, null=True)
#     martes2 = models.CharField(blank=True, null=True)
#     miercoles1 = models.CharField(blank=True, null=True)
#     miercoles2 = models.CharField(blank=True, null=True)
#     jueves1 = models.CharField(blank=True, null=True)
#     jueves2 = models.CharField(blank=True, null=True)
#     viernes1 = models.CharField(blank=True, null=True)
#     viernes2 = models.CharField(blank=True, null=True)
#     sabado1 = models.CharField(blank=True, null=True)
#     sabado2 = models.CharField(blank=True, null=True)
#     domingo1 = models.CharField(blank=True, null=True)
#     domingo2 = models.CharField(blank=True, null=True)
#     horareceso = models.DateTimeField(blank=True, null=True)

#     class Meta:
#      
#         db_table = 'jornadas'


class Liquidacion(models.Model):
    """
    
    """
    idliquidacion = models.AutoField(primary_key=True) #models.AutoField(primary_key=True)
    diastrabajados = models.CharField(max_length=8, blank=True, null=True)
    cesantias = models.CharField(max_length=30, blank=True, null=True)
    prima = models.CharField(max_length=30, blank=True, null=True)
    vacaciones = models.CharField(max_length=30, blank=True, null=True)
    intereses = models.CharField(max_length=30, blank=True, null=True)
    totalliq = models.CharField(max_length=30, blank=True, null=True)
    diascesantias = models.CharField(max_length=8, blank=True, null=True)
    diasprimas = models.CharField(max_length=8, blank=True, null=True)
    diasvacaciones = models.CharField(max_length=8, blank=True, null=True)
    baseprima = models.CharField(max_length=30, blank=True, null=True)
    basecesantias = models.CharField(max_length=30, blank=True, null=True)
    basevacaciones = models.CharField(max_length=30, blank=True, null=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING) #fk principal 
    fechainiciocontrato = models.DateField()
    fechafincontrato = models.DateField()
    salario = models.IntegerField()
    motivoretiro = models.CharField(max_length=100)# choice 
    estadoliquidacion = models.BooleanField(default=False)# boleano 
    diassusp = models.SmallIntegerField(blank=True, null=True)
    indemnizacion = models.IntegerField(blank=True, null=True)
    diassuspv = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'liquidacion'
        unique_together = (('idliquidacion', 'idcontrato'),)


class LiquidacionMasivo(models.Model):
    """
    estructura igual Liquidacion
    """
    idliquidacion = models.AutoField(primary_key=True) #models.AutoField(primary_key=True)
    diastrabajados = models.CharField(max_length=8, blank=True, null=True)
    cesantias = models.CharField(max_length=30, blank=True, null=True)
    prima = models.CharField(max_length=30, blank=True, null=True)
    vacaciones = models.CharField(max_length=30, blank=True, null=True)
    intereses = models.CharField(max_length=30, blank=True, null=True)
    totalliq = models.CharField(max_length=30, blank=True, null=True)
    diascesantias = models.CharField(max_length=8, blank=True, null=True)
    diasprimas = models.CharField(max_length=8, blank=True, null=True)
    diasvacaciones = models.CharField(max_length=8, blank=True, null=True)
    baseprima = models.CharField(max_length=30, blank=True, null=True)
    basecesantias = models.CharField(max_length=30, blank=True, null=True)
    basevacaciones = models.CharField(max_length=30, blank=True, null=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING) #fk principal 
    fechainiciocontrato = models.DateField()
    fechafincontrato = models.DateField()
    salario = models.IntegerField()
    motivoretiro = models.CharField(max_length=100)# choice 
    estadoliquidacion = models.BooleanField(default=False)# boleano 
    diassusp = models.SmallIntegerField(blank=True, null=True)
    indemnizacion = models.IntegerField(blank=True, null=True)
    diassuspv = models.SmallIntegerField(blank=True, null=True)
    
    
    class Meta:
        db_table = 'liquidacion_masivo'
        unique_together = (('idliquidacion', 'idcontrato'),)


class Mediospago(models.Model):
    """
    medios de pago - validar con fer 
    """
    cod_dian = models.SmallIntegerField(blank=True, null=True)
    medio = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'mediospago'





class NeDatosMensual(models.Model):
    idnominaelectronica = models.AutoField(primary_key=True)
    fechaliquidacioninicio = models.DateField(blank=True, null=True)
    fechaliquidacionfin = models.DateField(blank=True, null=True)
    fechageneracion = models.DateField(blank=True, null=True)
    prefijo = models.CharField(max_length=3, blank=True, null=True)
    consecutivo = models.IntegerField(blank=True, null=True)
    paisgeneracion = models.CharField(max_length=2, blank=True, null=True)
    departamentogeneracion = models.CharField(max_length=4, blank=True, null=True)
    ciudadgeneracion = models.CharField(max_length=10, blank=True, null=True)
    idioma = models.CharField(max_length=4, blank=True, null=True)
    horageneracion = models.TimeField(blank=True, null=True)
    periodonomina = models.CharField(max_length=1, blank=True, null=True)
    tipomoneda = models.CharField(max_length=3, blank=True, null=True)
    fechapago = models.DateField(blank=True, null=True)
    ciudaddepartamento = models.CharField(max_length=3, blank=True, null=True)
    mesacumular = models.CharField(max_length=40, blank=True, null=True)
    anoacumular = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        db_table = 'ne_datos_mensual'


class NeDetalleNominaElectronica(models.Model):
    id_detalle_nomina_electronica = models.AutoField(primary_key=True)
    id_ne_datos_mensual = models.ForeignKey(NeDatosMensual, models.DO_NOTHING, blank=True, null=True)
    id_contrato = models.IntegerField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_modificacion = models.DateTimeField(blank=True, null=True)
    json_nomina = models.TextField(blank=True, null=True)
    estado = models.IntegerField(blank=True, null=True)
    tipo_registro = models.IntegerField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'ne_detalle_nomina_electronica'


class NeRespuestaDian(models.Model):
    id_ne_respuesta_dian = models.AutoField(primary_key=True)
    id_ne_detalle_nomina_electronica = models.ForeignKey(NeDetalleNominaElectronica, models.DO_NOTHING, blank=True, null=True)
    fecha_transaccion = models.DateTimeField(blank=True, null=True)
    json_respuesta = models.TextField(blank=True, null=True)
    codigo_respuesta = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'ne_respuesta_dian'


class NeSumatorias(models.Model):
    ne_id = models.CharField(primary_key=True, max_length=8)
    campo = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'ne_sumatorias'





class Nomina(models.Model):
    """
    
    """
    idregistronom = models.AutoField(primary_key=True) ##models.AutoField(primary_key=True)
    valor = models.IntegerField(blank=True, null=True)
    cantidad = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    idconcepto = models.ForeignKey(Conceptosdenomina, models.DO_NOTHING ) 
    idnomina = models.ForeignKey(Crearnomina, models.DO_NOTHING ) 
    estadonomina = models.SmallIntegerField(blank=True, null=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING , blank=True, null=True)
    idcosto = models.ForeignKey(Costos, models.DO_NOTHING , blank=True, null=True)
    idsubcosto = models.ForeignKey('Subcostos', models.DO_NOTHING  ,blank=True, null=True)
    control = models.IntegerField(blank=True, null=True) # vacaciones o incapacidades o prestamos automatico  

    class Meta:
        db_table = 'nomina'


class NominaComprobantes(models.Model):
    """
    historico de nomina 
    otro planteamento 
    """
    idhistorico = models.AutoField(primary_key=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING, blank=True, null=True) # enlace a contrato 
    salario = models.IntegerField(blank=True, null=True)
    cargo = models.CharField(max_length=120, blank=True, null=True)
    idcosto = models.ForeignKey(Costos, models.DO_NOTHING,blank=True, null=True)# enlace a costos 
    pension = models.CharField(max_length=125, blank=True, null=True)
    salud = models.CharField(max_length=125, blank=True, null=True) 
    idnomina = models.ForeignKey(Crearnomina, models.DO_NOTHING)
    envio_email = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'nomina_comprobantes'


class NominaFija(models.Model):
    """
    quieta y se valida si se usa o no 
    
    """
    idregistronom = models.AutoField(primary_key=True)
    idnomina = models.CharField(max_length=255, blank=True, null=True)# enlace a nomina 
    nombreconcepto = models.CharField(max_length=255, blank=True, null=True)
    valor = models.DecimalField(max_digits=11, decimal_places=1, blank=True, null=True)
    mesacumular = models.CharField(max_length=15, blank=True, null=True)# qui
    anoacumular = models.CharField(max_length=15, blank=True, null=True)#
    multiplicadorconcepto = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    cantidad = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    idconcepto = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'nomina_fija'


class NominaImportador(models.Model):
    """
    igualar a nomina 
    """
    idregistronom = models.AutoField(primary_key=True) ##models.AutoField(primary_key=True)
    valor = models.IntegerField(blank=True, null=True)
    cantidad = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    idconcepto = models.ForeignKey(Conceptosdenomina, models.DO_NOTHING) 
    idnomina = models.ForeignKey(Crearnomina, models.DO_NOTHING) 
    estadonomina = models.SmallIntegerField(blank=True, null=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING)
    idcosto = models.ForeignKey(Costos, models.DO_NOTHING)
    idsubcosto = models.ForeignKey('Subcostos', models.DO_NOTHING)
    control = models.IntegerField(blank=True, null=True) # vacaciones o incapacidades o prestamos automatico  

    class Meta:
        db_table = 'nomina_importador'


class NovCambiocargo(models.Model):
    """
    igual 
    """
    idcambiocargo = models.AutoField(primary_key=True)
    idcontrato = models.IntegerField(blank=True, null=True)
    idempleado = models.IntegerField(blank=True, null=True)#quitar 
    cargoactual = models.CharField(max_length=50, blank=True, null=True)#enlace
    nuevocargo = models.CharField(max_length=50, blank=True, null=True)#enlace
    fechacargo = models.DateField(blank=True, null=True)
    aprobar = models.CharField(max_length=1, blank=True, null=True)#quitar 
    ccostoactual = models.CharField(max_length=30, blank=True, null=True)#enlace
    nuevoccosto = models.CharField(max_length=30, blank=True, null=True)#enlace
    subccostoactual = models.CharField(max_length=30, blank=True, null=True)#enlace
    fechaccosto = models.DateField(blank=True, null=True)
    nuevosubcosto = models.CharField(max_length=30, blank=True, null=True)
    fechasubcosto = models.DateField(blank=True, null=True)
    empleado = models.CharField(max_length=40, blank=True, null=True)#quitar 
    centrotrabajoactual = models.CharField(max_length=30, blank=True, null=True)#enlace
    nuevocentrotrabajo = models.CharField(max_length=30, blank=True, null=True)#enlace
    fechacentrotrabajo = models.DateField(blank=True, null=True)
    sedeactual = models.CharField(max_length=30, blank=True, null=True)#enlace
    nuevasede = models.CharField(max_length=30, blank=True, null=True)#enlace
    fechanuevasede = models.DateField(blank=True, null=True)
    estadonovcambio = models.SmallIntegerField(blank=True, null=True)#quitar

    class Meta:
        db_table = 'nov_cambiocargo'


class NovDescuentos(models.Model):
    """
    igual 
    """
    idnovdescuento = models.AutoField(primary_key=True)
    idempleado = models.IntegerField(blank=True, null=True)
    idcontrato = models.IntegerField(blank=True, null=True)
    empleado = models.CharField(max_length=50, blank=True, null=True)
    conceptodescuento = models.CharField(max_length=50, blank=True, null=True)
    valordescuento = models.IntegerField(blank=True, null=True)
    fechanovedad = models.DateField(blank=True, null=True)
    idnomina = models.IntegerField(blank=True, null=True)
    estadonovdes = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'nov_descuentos'


class NovFijos(models.Model):
    """
    
    """
    idnovfija = models.AutoField(primary_key=True)
    idconcepto = models.ForeignKey(Conceptosdenomina, models.DO_NOTHING)  
    valor = models.IntegerField(blank=True, null=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING)  #fk principal 
    estado_novfija = models.BooleanField(default=False) #boleano 
    pago = models.CharField(max_length=40, blank=True, null=True)
    diapago = models.SmallIntegerField(blank=True, null=True)
    descripcion = models.CharField(max_length=40, blank=True, null=True)
    fechafinnovedad = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'nov_fijos'


class NovSalarios(models.Model):
    """
    
    """
    idcambiosalario = models.AutoField(primary_key=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING) 
    salarioactual = models.IntegerField(blank=True, null=True)# automatico 
    nuevosalario = models.IntegerField(blank=True, null=True)#manual 
    fechanuevosalario = models.DateField(blank=True, null=True)
    tiposalario = models.SmallIntegerField(blank=True, null=True)#enlace tiposalarios 

    class Meta:
        db_table = 'nov_salarios'


class NovSegsocial(models.Model):
    """
    validar cambio de eps o pension modificar 
    
    """
    idcambiosegsocial = models.AutoField(primary_key=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING) #fk principal 
    epsactual = models.CharField(max_length=40, blank=True, null=True)#automatico
    nuevaeps = models.CharField(max_length=40, blank=True, null=True)#manual
    fechaeps = models.DateField(blank=True, null=True)
    afpactual = models.CharField(max_length=40, blank=True, null=True)#automatico
    nuevaafp = models.CharField(max_length=40, blank=True, null=True)#manual
    fechaafp = models.DateField(blank=True, null=True)
    codeps = models.CharField(max_length=10, blank=True, null=True)
    codafp = models.CharField(max_length=10, blank=True, null=True)
    estadonov = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'nov_segsocial'




# class Pila(models.Model):
#     """
#     proixima a validar informacion de pila 
#     """
#     idaportes = models.IntegerField(primary_key=True) 
#     docidentidad = models.BigIntegerField()
#     salario = models.CharField(max_length=8, blank=True, null=True)
#     mesacumular = models.CharField(max_length=15, blank=True, null=True)
#     anoacumular = models.CharField(max_length=15, blank=True, null=True)
#     basesegsocial = models.IntegerField(blank=True, null=True)
#     diaseps = models.CharField(max_length=6, blank=True, null=True)
#     diasafp = models.IntegerField(blank=True, null=True)
#     diasarl = models.IntegerField(blank=True, null=True)
#     diasccf = models.IntegerField(blank=True, null=True)
#     diasincapeps = models.IntegerField(blank=True, null=True)
#     diasincaparl = models.IntegerField(blank=True, null=True)
#     numautincapeps = models.IntegerField(blank=True, null=True)
#     valincapeps = models.IntegerField(blank=True, null=True)
#     diaslicmat = models.IntegerField(blank=True, null=True)
#     numautlicmat = models.IntegerField(blank=True, null=True)
#     vallicmat = models.IntegerField(blank=True, null=True)
#     valeps = models.IntegerField(blank=True, null=True)
#     valafp = models.IntegerField(blank=True, null=True)
#     valarl = models.IntegerField(blank=True, null=True)
#     valccf = models.IntegerField(blank=True, null=True)
#     valicbf = models.IntegerField(blank=True, null=True)
#     valsena = models.IntegerField(blank=True, null=True)
#     tareps = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
#     tarifaarl = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
#     tarafp = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
#     tarccf = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
#     tarsena = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
#     taricbf = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
#     eps = models.CharField(max_length=50, blank=True, null=True)
#     pension = models.CharField(max_length=50, blank=True, null=True)
#     total = models.IntegerField(blank=True, null=True)

#     class Meta:
#      
#         db_table = 'pila'
#         unique_together = (('idaportes', 'docidentidad'),)


# class PilaConceptos(models.Model):
#     """
#     proixima a validar informacion de pila 
#     """
#     idnov = models.CharField(max_length=6)
#     nombre_novedad = models.CharField(max_length=70, blank=True, null=True)

#     class Meta:
#      
#         db_table = 'pila_conceptos'


# class PilaContenedor(models.Model):
#     """
#     proixima a validar informacion de pila 
#     """
#     id_pila_contenedor = models.AutoField(primary_key=True)
#     estado = models.IntegerField()
#     mes = models.CharField()
#     anio = models.CharField()
#     fecha_pago = models.DateField(blank=True, null=True)
#     archivo_generado = models.CharField(blank=True, null=True)
#     tamanio_archivo = models.CharField(blank=True, null=True)
#     fecha_generacion = models.DateTimeField(blank=True, null=True)

#     class Meta:
#      
#         db_table = 'pila_contenedor'


# class PilaEstado(models.Model):
#     """
#     proixima a validar informacion de pila 
#     """
#     id_pila_estado = models.AutoField(primary_key=True)
#     nombre_estado_pila = models.CharField(max_length=32)

#     class Meta:
#      
#         db_table = 'pila_estado'


# class PilaFijos(models.Model):
#     """
#     proixima a validar informacion de pila 
#     """
#     idfix = models.BigAutoField()
#     docidentidad = models.CharField(max_length=40, blank=True, null=True)
#     idcontrato = models.CharField(max_length=7, blank=True, null=True)
#     diaspension = models.SmallIntegerField(blank=True, null=True)
#     diassalud = models.SmallIntegerField(blank=True, null=True)
#     diasarl = models.SmallIntegerField(blank=True, null=True)
#     diasccf = models.SmallIntegerField(blank=True, null=True)
#     salariobasico = models.SmallIntegerField(blank=True, null=True)
#     ibcpension = models.SmallIntegerField(blank=True, null=True)
#     ibcsalud = models.SmallIntegerField(blank=True, null=True)
#     ibcarl = models.SmallIntegerField(blank=True, null=True)
#     ibcccf = models.SmallIntegerField(blank=True, null=True)
#     tarpen = models.SmallIntegerField(blank=True, null=True)
#     cotpen = models.SmallIntegerField(blank=True, null=True)
#     apvolpen = models.SmallIntegerField(blank=True, null=True)
#     apvolpenemp = models.SmallIntegerField(blank=True, null=True)
#     totalcotpen = models.SmallIntegerField(blank=True, null=True)
#     fsp = models.SmallIntegerField(blank=True, null=True)
#     fspsub = models.SmallIntegerField(blank=True, null=True)
#     noretapvol = models.SmallIntegerField(blank=True, null=True)
#     tarsalud = models.SmallIntegerField(blank=True, null=True)
#     cotsalud = models.SmallIntegerField(blank=True, null=True)
#     upc = models.SmallIntegerField(blank=True, null=True)
#     tararl = models.SmallIntegerField(blank=True, null=True)
#     centrotrabajo = models.SmallIntegerField(blank=True, null=True)
#     cotarl = models.SmallIntegerField(blank=True, null=True)
#     tarccf = models.SmallIntegerField(blank=True, null=True)
#     apccf = models.SmallIntegerField(blank=True, null=True)
#     tarsena = models.SmallIntegerField(blank=True, null=True)
#     apsena = models.SmallIntegerField(blank=True, null=True)
#     taricbf = models.SmallIntegerField(blank=True, null=True)
#     apicbf = models.SmallIntegerField(blank=True, null=True)
#     taresap = models.SmallIntegerField(blank=True, null=True)
#     apesap = models.SmallIntegerField(blank=True, null=True)
#     tarmen = models.SmallIntegerField(blank=True, null=True)
#     apmen = models.SmallIntegerField(blank=True, null=True)
#     ley1607 = models.CharField(max_length=1, blank=True, null=True)
#     mesacumular = models.CharField(max_length=10, blank=True, null=True)
#     anoacumular = models.CharField(max_length=4, blank=True, null=True)

#     class Meta:
#      
#         db_table = 'pila_fijos'


# class PilaNovedades(models.Model):
    
#     """
#     proixima a validar informacion de pila 
#     """
#     idnov = models.AutoField()
#     docidentidad = models.IntegerField(blank=True, null=True)
#     idcontrato = models.IntegerField(blank=True, null=True)
#     mesacumular = models.CharField(max_length=20, blank=True, null=True)
#     anoacumular = models.CharField(max_length=8, blank=True, null=True)
#     tiponovedad = models.CharField(max_length=10, blank=True, null=True)
#     valortotal = models.IntegerField(blank=True, null=True)
#     ajustarnovedad = models.CharField(max_length=2, blank=True, null=True)
#     realizarparafiscales = models.CharField(max_length=2, blank=True, null=True)
#     diainicial = models.SmallIntegerField(blank=True, null=True)
#     diaduracion = models.SmallIntegerField(blank=True, null=True)
#     tipoingresoretiro = models.SmallIntegerField(blank=True, null=True)
#     vstccf = models.CharField(max_length=2, blank=True, null=True)
#     vstsenaicbf = models.CharField(max_length=2, blank=True, null=True)
#     ige100 = models.CharField(max_length=16, blank=True, null=True)
#     slntipo = models.CharField(max_length=30, blank=True, null=True)
#     slntarifapension = models.CharField(max_length=30, blank=True, null=True)
#     vactipo = models.CharField(max_length=30, blank=True, null=True)
#     vhl = models.SmallIntegerField(blank=True, null=True)
#     tipoid = models.CharField(max_length=2, blank=True, null=True)

#     class Meta:
#      
#         db_table = 'pila_novedades'


class Prestamos(models.Model):
    idprestamo = models.AutoField(primary_key=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING) # fk principal 
    valorprestamo = models.IntegerField(blank=True, null=True) 
    fechaprestamo = models.DateField(blank=True, null=True)
    cuotasprestamo = models.SmallIntegerField(blank=True, null=True)
    valorcuota = models.IntegerField(blank=True, null=True)
    estadoprestamo = models.BooleanField(default=False)#boleano
    
    class Meta:
        db_table = 'prestamos'





class ProvisionesContables(models.Model):
    """
    
    """
    idregistronom = models.AutoField(primary_key=True)
    valor = models.IntegerField(blank=True, null=True)
    mesacumular = models.CharField(max_length=15, blank=True, null=True)
    anoacumular = models.CharField(max_length=15, blank=True, null=True)
    idconcepto = models.ForeignKey(Conceptosdenomina, models.DO_NOTHING) 
    idcontrato =  models.ForeignKey(Contratos, models.DO_NOTHING) 
    idcosto =  models.ForeignKey(Costos, models.DO_NOTHING ) 
    entidad = models.CharField(max_length=32, blank=True, null=True) # nit 

    class Meta:
        db_table = 'provisiones_contables'


class Salariominimoanual(models.Model):
    #se deja igual 
    idano = models.AutoField(primary_key=True)
    salariominimo = models.IntegerField(blank=True, null=True)
    auxtransporte = models.IntegerField(blank=True, null=True)
    uvt = models.IntegerField(blank=True, null=True)
    ano = models.IntegerField(blank=True, null=True)
    
    class Meta:
        db_table = 'salariominimoanual'


class SalariosImportador(models.Model):
    """
    cambio masivo se valida mas adelante 
    """
    id_salario = models.AutoField(primary_key=True)
    docidentidad = models.IntegerField(blank=True, null=True)
    nuevosalario = models.IntegerField(blank=True, null=True)
    fechanuevosalario = models.DateField(blank=True, null=True)
    tiposalario = models.SmallIntegerField(blank=True, null=True)
    idcontrato = models.IntegerField(blank=True, null=True)
    idempleado = models.IntegerField(blank=True, null=True)
    salarioanterior = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'salarios_importador'






# class Tiempos(models.Model):
#     """
#     validar con aplicativo reloj 
#     """
#     idmarcacion = models.AutoField(primary_key=True)
#     fechaingreso = models.DateField(blank=True, null=True)
#     horaingreso = models.TimeField(blank=True, null=True)
#     horasalida = models.TimeField(blank=True, null=True)
#     horasdescuentos = models.TimeField(blank=True, null=True)
#     idcontrato = models.IntegerField(blank=True, null=True)
#     idnomina = models.IntegerField(blank=True, null=True)
#     fechasalida = models.DateField(blank=True, null=True)
#     horasord = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     horastrab = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     horasdomfes = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     hed = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     hen = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     hedf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     henf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     rn = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     rnf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     dyf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     sede = models.CharField(max_length=100, blank=True, null=True)
#     fechaturno = models.DateField(blank=True, null=True)#quitar
#     saldo = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)#quitar

#     class Meta:
#         db_table = 'tiempos'


# class TiemposTotales(models.Model):
#     idtiempostotales = models.IntegerField(primary_key=True)
#     idcontrato = models.IntegerField(blank=True, null=True)#fk principal 
#     horasord = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     horastrab = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     horasdomfes = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     hed = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     vhed = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
#     hen = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     vhen = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
#     hedf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     vhedf = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     henf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     vhenf = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     rn = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     vrn = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     rnf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     vrnf = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     dyf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     vdyf = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     idnomina = models.SmallIntegerField(blank=True, null=True)#enlace nomina 
#     valorextras = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     empleado = models.CharField(max_length=60, blank=True, null=True)#quitar
#     sede = models.CharField(max_length=60, blank=True, null=True)# enlace sede 
#     saldo = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)#quitar 
#     idcosto = models.CharField(max_length=3, blank=True, null=True)# enlace costo 
#     idsubcosto = models.CharField(max_length=3, blank=True, null=True)# enlace subcosto

#     class Meta:
#         db_table = 'tiempos_totales'

# validar 
class Vacaciones(models.Model):
    idvacaciones = models.IntegerField(primary_key=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING, blank=True, null=True)
    fechainicialvac = models.DateField(blank=True, null=True)
    ultimodiavac = models.DateField(blank=True, null=True)
    diascalendario = models.SmallIntegerField(blank=True, null=True)
    diasvac = models.SmallIntegerField(blank=True, null=True)
    diaspendientes = models.SmallIntegerField(blank=True, null=True)
    pagovac = models.IntegerField(blank=True, null=True)
    totaldiastomados = models.SmallIntegerField(blank=True, null=True)
    basepago = models.IntegerField(blank=True, null=True)
    estadovac = models.SmallIntegerField(blank=True, null=True)
    idnomina = models.ForeignKey(Crearnomina, models.DO_NOTHING ) 
    cuentasabados = models.SmallIntegerField(blank=True, null=True)
    tipovac = models.ForeignKey(Tipoavacaus, models.DO_NOTHING )
    idvacmaster = models.IntegerField(blank=True, null=True)
    perinicio = models.DateField(blank=True, null=True)
    perfinal = models.DateField(blank=True, null=True)
    fechapago = models.DateField(blank=True, null=True)

    class Meta :

        db_table = 'vacaciones'


# class VacacionesImportador(models.Model):
#     #igual vacaciones 
#     id_reg = models.AutoField(primary_key=True)
#     cedula = models.BigIntegerField(blank=True, null=True)
#     idconcepto = models.SmallIntegerField(blank=True, null=True)
#     fechainicialvac = models.DateField(blank=True, null=True)
#     ultimodiavac = models.DateField(blank=True, null=True)
#     diasvac = models.SmallIntegerField(blank=True, null=True)
#     sabados = models.SmallIntegerField(blank=True, null=True)
#     perinicio = models.DateField(blank=True, null=True)
#     perfinal = models.DateField(blank=True, null=True)
#     idnomina = models.BigIntegerField(blank=True, null=True)
#     idcontrato = models.BigIntegerField(blank=True, null=True)
#     idempleado = models.BigIntegerField(blank=True, null=True)
#     pagovac = models.IntegerField(blank=True, null=True)
#     basepago = models.IntegerField(blank=True, null=True)
#     tipovac = models.SmallIntegerField(blank=True, null=True)
#     fechapago = models.DateField(blank=True, null=True)
#     tiponovedad = models.SmallIntegerField(blank=True, null=True)
#     idvacaciones = models.IntegerField(blank=True, null=True)
#     idvacmaster = models.IntegerField(blank=True, null=True)
#     estadovac = models.SmallIntegerField(blank=True, null=True)
#     diascalendario = models.IntegerField(blank=True, null=True)

#     class Meta:
#      
#         db_table = 'vacaciones_importador'


# class VacacionesMaster(models.Model):
#     #considerar eliminar 
#     idvacmaster = models.IntegerField(primary_key=True)
#     idcontrato = models.SmallIntegerField(blank=True, null=True) #fk principal 
#     empleado = models.CharField(blank=True, null=True)# 
#     titulovac = models.CharField(blank=True, null=True)
#     fechapago = models.DateField(blank=True, null=True)

#     class Meta:
#      
#         db_table = 'vacaciones_master'


# class Zcuentasbancos(models.Model):
#     #considerar eliminar 
#     idcontrato = models.SmallIntegerField(primary_key=True)
#     cuentanomina = models.CharField(max_length=255, blank=True, null=True)
#     bancocuenta = models.CharField(max_length=255, blank=True, null=True)
#     tipocuentanomina = models.CharField(max_length=255, blank=True, null=True)

#     class Meta:
#      
#         db_table = 'zcuentasbancos'


