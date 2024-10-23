from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class Empresa(models.Model):
    ##models.AutoField(primary_key=True)
    idempresa = models.CharField(primary_key=True, max_length=10)#models.AutoField(primary_key=True)
    nit = models.CharField(max_length=20)
    nombreempresa = models.CharField(max_length=255, blank=True, null=True)
    dv = models.CharField(max_length=10, blank=True, null=True)# Dígito de verificación del NIT
    tipodoc = models.CharField(max_length=2, blank=True, null=True)# Tipo de documento de empresa NI O CC o PP
    # Representante legal
    replegal = models.CharField(max_length=255, blank=True, null=True)

    # Datos de contacto principales
    direccionempresa = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=30, blank=True, null=True)
    ciudad = models.CharField(max_length=255, blank=True, null=True)#Posible enlace  quitar 
    codciudad = models.CharField(max_length=10, blank=True, null=True)# Posible enlace ->ciudades  
    nomciudad = models.CharField(max_length=255, blank=True, null=True)# redundante  quitar 
    coddpto = models.CharField(max_length=10, blank=True, null=True)  # Código del departamento #redundante quitar 
    pais = models.CharField(max_length=80, blank=True, null=True)
    
    

    # Detalles de ARL y códigos relacionados
    arl = models.CharField(max_length=255, blank=True, null=True)#Posible enlace 
    codarl = models.CharField(max_length=15, blank=True, null=True)#redundante quitar 

    # Detalles de nómina y RRHH #redundante  posible nueva tabla 
    contactonomina = models.CharField(max_length=50, blank=True, null=True)
    emailnomina = models.CharField(max_length=50, blank=True, null=True)
    contactorrhh = models.CharField(max_length=50, blank=True, null=True)
    emailrrhh = models.CharField(max_length=50, blank=True, null=True)

    # Contabilidad y certificaciones 
    contactocontab = models.CharField(max_length=50, blank=True, null=True)
    emailcontab = models.CharField(max_length=50, blank=True, null=True)
    
    
    cargocertificaciones = models.CharField(max_length=50, blank=True, null=True)
    firmacertificaciones = models.CharField(max_length=50, blank=True, null=True)

    # Detalles adicionales
    website = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=40, blank=True, null=True)
    metodoextras = models.CharField(max_length=255, blank=True, null=True)
    idcliente = models.SmallIntegerField(blank=True, null=True)#redundante quitar 
    bdatos = models.CharField(max_length=20, blank=True, null=True)#redundante quitar 

    # Campos relacionados con aportes y parafiscales
    realizarparafiscales = models.CharField(max_length=2, blank=True, null=True)
    vstccf = models.CharField(max_length=2, blank=True, null=True)
    vstsenaicbf = models.CharField(max_length=2, blank=True, null=True)
    ige100 = models.CharField(max_length=2, blank=True, null=True)
    slntarifapension = models.CharField(max_length=2, blank=True, null=True)

    # Detalles bancarios
    banco = models.CharField(max_length=3, blank=True, null=True) #Posible enlace
    numcuenta = models.CharField(max_length=255, blank=True, null=True)
    tipocuenta = models.CharField(max_length=10, blank=True, null=True)

    # Sucursales y aportantes #redundante y posible nueva tabla 
    codigosuc = models.CharField(max_length=10, blank=True, null=True)
    nombresuc = models.CharField(max_length=40, blank=True, null=True)
    claseaportante = models.CharField(max_length=1, blank=True, null=True)
    tipoaportante = models.SmallIntegerField(blank=True, null=True)
    
    ajustarnovedad = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empresa'


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"


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

class CustomUser(AbstractBaseUser):
    TIPO_USER_CHOICES = [
        ('admin', 'Administrator'),
        ('employee', 'Employee'),
        ('company', 'Company'),
        ('accountant', 'Accountant'),
    ]


    email = models.EmailField(unique=True)
    tipo_user = models.CharField(max_length=10, choices=TIPO_USER_CHOICES, default='interno')
    rol = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    id_empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} - {self.tipo_user}"

    def is_admin(self):
        return self.role == 'admin'

    def is_normal(self):
        return self.role == 'normal'


## modelos normales 
"""
Posible cambio de nombre 
posible cambio de nombre - columnas 

"""

class Anos(models.Model):
    """
    tabla de años , actualmente no usada por tablas con campo de año 
    """
    idano = models.IntegerField(primary_key=True) #models.AutoField(primary_key=True)
    ano = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'anos'


class Ausencias(models.Model):
    """
    tabla no conocida 
    """
    idausencia = models.SmallIntegerField(primary_key=True) #int 
    ausencia = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ausencias'

class Ausentismo(models.Model):
    """
    tabla no conocida 
    
    fk 
    idempleado
    idcontrato
    idnomina
    
    Pendiente de validacion : uso 
    """
    
    idausentismo = models.IntegerField(primary_key=True)#models.AutoField(primary_key=True)
    ausencia = models.CharField(max_length=255, blank=True, null=True) # id ausensia 
    remunerado = models.CharField(max_length=5, blank=True, null=True)# boleano 
    horasdescontar = models.IntegerField(blank=True, null=True) 
    idempleado = models.IntegerField(blank=True, null=True) #redundante quitar 
    idcontrato = models.IntegerField(blank=True, null=True) #enlace pincipal 
    fechanovedad = models.DateField(blank=True, null=True)
    empleado = models.CharField(max_length=50, blank=True, null=True) #redundante quitar 
    autorizadopor = models.CharField(max_length=50, blank=True, null=True)# Posible enlace 
    hasta = models.DateField(blank=True, null=True)#quitar 
    horainicio = models.TimeField(blank=True, null=True)
    horafin = models.TimeField(blank=True, null=True)
    horasausencia = models.IntegerField(blank=True, null=True) # texto 
    estadoausentismo = models.SmallIntegerField(blank=True, null=True)# Cambio de tipo 
    idnomina = models.IntegerField(blank=True, null=True)#Posible enlace 

    class Meta:
        managed = False
        db_table = 'ausentismo'
        

class Bancos(models.Model):
    """
    enlace contratos y empresas 
    """
    idbanco = models.IntegerField(primary_key=True)#models.AutoField(primary_key=True)
    nombanco = models.CharField(max_length=255, blank=True, null=True)
    codbanco = models.CharField(max_length=255, blank=True, null=True)
    codach = models.CharField(max_length=255, blank=True, null=True)
    digchequeo = models.CharField(max_length=255, blank=True, null=True)
    nitbanco = models.CharField(max_length=255, blank=True, null=True)
    tamcorriente = models.CharField(max_length=255, blank=True, null=True)
    tamahorro = models.CharField(max_length=255, blank=True, null=True)
    oficina = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'bancos'


class Cargos(models.Model):
    """
    tabla De cargos 
    
    requiere relacion de empresa 
    requiere relacion de cargo jefe y cargo por debajo 
    requiere validacion de nombrenivel 
    
    """
    idcargo = models.AutoField(primary_key=True)#models.AutoField(primary_key=True)
    nombrecargo = models.CharField(max_length=50)
    nombrenivel = models.CharField(max_length=50, blank=True, null=True) # enlace a structura 
    cargojefe = models.CharField(max_length=50, blank=True, null=True) #quitar 
    cargosacargo = models.CharField(blank=True, null=True)#quitar 
    estado = models.BooleanField(blank=True, null=True)# por defecto true 

    class Meta:
        managed = False
        db_table = 'cargos'

"""
class Nivelesestructura(models.Model):
    idnivel = models.SmallIntegerField(primary_key=True)
    nombrenivel = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nivelesestructura'

"""


class Centrotrabajo(models.Model):
    """
    tabla De Centros de trabajo 
    
    debe ser usada en contratos 
    """
    nombrecentrotrabajo = models.CharField(max_length=30, blank=True, null=True)
    tarifaarl = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    centrotrabajo = models.SmallAutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'centrotrabajo'


class Certificaciones(models.Model):
    """
    tabla De Certificaciones 
    """
    idcert = models.AutoField(primary_key=True)
    destino = models.CharField(max_length=100, blank=True, null=True)
    idempleado = models.ForeignKey('Contratosemp', models.DO_NOTHING, db_column='idempleado', blank=True, null=True) #redundante
    idcontrato = models.IntegerField(blank=True, null=True) # mejor fk 
    fecha = models.DateField(blank=True, null=True)
    salario = models.IntegerField(blank=True, null=True)# fija requerido  
    cargo = models.CharField(max_length=100, blank=True, null=True)# fija requerido 
    tipocontrato = models.CharField(max_length=30, blank=True, null=True)# fija requerido 
    promediovariable = models.IntegerField(blank=True, null=True) # calculo  
    codigoconfirmacion = models.CharField(max_length=8, blank=True, null=True) 
    tipocertificacion = models.IntegerField(blank=True, null=True)
    

    class Meta:
        managed = False
        db_table = 'certificaciones'
        


class Cesantias(models.Model):
    """
    tabla no Conocida 
    """
    idces = models.IntegerField(primary_key=True) #models.AutoField(primary_key=True)
    idcontrato = models.IntegerField(blank=True, null=True)#Posible enlace 
    valcesa = models.IntegerField(blank=True, null=True)
    valint = models.IntegerField(blank=True, null=True)
    anoacumular = models.IntegerField(blank=True, null=True)# enlace a años  
    salario = models.IntegerField(blank=True, null=True)# calculado 
    transporte = models.IntegerField(blank=True, null=True)#calculado
    extras = models.IntegerField(blank=True, null=True)#calculado
    diascesa = models.IntegerField(blank=True, null=True)#calculado
    fondo = models.CharField(max_length=255, blank=True, null=True) # codigo fondo ces 
    estadoces = models.CharField(max_length=255, blank=True, null=True) # quitar 
    papellido = models.CharField(max_length=255, blank=True, null=True)#redundante quitar 
    sapellido = models.CharField(max_length=255, blank=True, null=True)#redundante quitar 
    pnombre = models.CharField(max_length=255, blank=True, null=True)#redundante quitar 
    snombre = models.CharField(max_length=255, blank=True, null=True)#redundante quitar  
    docidentidad = models.IntegerField(blank=True, null=True)#redundante quitar 
    fechainiciocontrato = models.DateTimeField(blank=True, null=True)#redundante quitar  
    valcesaacum = models.IntegerField(blank=True, null=True) # acomulado variable 
    diassuspension = models.IntegerField(blank=True, null=True) #  calcular 

    class Meta:
        managed = False
        db_table = 'cesantias'


class Ciudades(models.Model):
    """
    tabla de cidudades
    Usarla donde deberia 
    añadir pais o remplazar por una api 
    """
    idciudad = models.CharField(primary_key=True, max_length=10)
    ciudad = models.CharField(max_length=50, db_collation='es_ES', blank=True, null=True)
    departamento = models.CharField(max_length=50, db_collation='es_ES', blank=True, null=True)
    codciudad = models.CharField(max_length=10, blank=True, null=True)
    coddepartamento = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ciudades'


class Conceptosdenomina(models.Model):
    """
    tabla de Conceptosdenomina
    Buscar mejora 
    Idempresa
    """
    
    nombreconcepto = models.CharField(max_length=30)
    multiplicadorconcepto = models.DecimalField(max_digits=4, decimal_places=2)
    tipoconcepto = models.IntegerField()
    sueldobasico = models.IntegerField(blank=True, null=True)
    auxtransporte = models.IntegerField(blank=True, null=True)
    baseprestacionsocial = models.IntegerField(blank=True, null=True)
    ingresotributario = models.IntegerField(blank=True, null=True)
    prestacionsocial = models.IntegerField(blank=True, null=True)
    extras = models.IntegerField(blank=True, null=True)
    basesegsocial = models.IntegerField(blank=True, null=True)
    cuentacontable = models.CharField(max_length=25, blank=True, null=True)
    idconcepto = models.IntegerField(primary_key=True)
    ausencia = models.IntegerField(blank=True, null=True)
    salintegral = models.IntegerField(blank=True, null=True)
    basevacaciones = models.IntegerField(blank=True, null=True)
    formula = models.CharField(max_length=1, blank=True, null=True)
    basetransporte = models.SmallIntegerField(blank=True, null=True)
    aportess = models.SmallIntegerField(blank=True, null=True)
    incapacidad = models.SmallIntegerField(blank=True, null=True)
    base1393 = models.SmallIntegerField(blank=True, null=True)
    norenta = models.SmallIntegerField(blank=True, null=True)
    pension = models.SmallIntegerField(blank=True, null=True)
    exentos = models.SmallIntegerField(blank=True, null=True)
    baserarl = models.SmallIntegerField(blank=True, null=True)
    basecaja = models.SmallIntegerField(blank=True, null=True)
    viaticos = models.SmallIntegerField(blank=True, null=True)
    comisiones = models.SmallIntegerField(blank=True, null=True)
    gastosderep = models.SmallIntegerField(blank=True, null=True)
    suspcontrato = models.SmallIntegerField(blank=True, null=True)
    grupo_dian = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'conceptosdenomina'


class Conceptosfijos(models.Model):
    """
    tabla de Conceptosfijos
    Usarla donde deberia 
    """
    idfijo = models.IntegerField(primary_key=True)
    conceptofijo = models.CharField(max_length=80, blank=True, null=True)
    valorfijo = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'conceptosfijos'


class Contabcuentas(models.Model):
    """
    tabla de Contabcuentas
    Usarla donde deberia 
    Idempresa  
    quitar :idcuentacontable = 1 y idcuentacontable = 2 
    """
    
    idcuentacontable = models.CharField(max_length=12, blank=True, null=True)
    cuentacontable = models.CharField(max_length=50, blank=True, null=True)
    idcuenta = models.CharField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'contabcuentas'


class Contabgrupos(models.Model):
    """
    tabla de Contabgrupos
    Usarla donde deberia 
    """
    idgrupo = models.CharField(primary_key=True, max_length=2)
    grupocontable = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contabgrupos'


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
    cargo = models.CharField(max_length=50, blank=True, null=True)# enlace cargo 
    fechainiciocontrato = models.DateField(blank=True, null=True)
    fechafincontrato = models.DateField(blank=True, null=True)
    tipocontrato = models.IntegerField(blank=True, null=True)# enlace tipocontrato
    tiponomina = models.CharField(max_length=12, blank=True, null=True)# enlace enlace
    bancocuenta = models.CharField(max_length=30, blank=True, null=True)# enlace banco
    cuentanomina = models.CharField(max_length=30, blank=True, null=True) 
    tipocuentanomina = models.CharField(max_length=15, blank=True, null=True) # choice agreagar deposito electronico 
    eps = models.CharField(max_length=125, blank=True, null=True)#quitar 
    pension = models.CharField(max_length=125, blank=True, null=True)#quitar 
    cajacompensacion = models.CharField(max_length=40, blank=True, null=True)#quitar 
    centrotrabajo = models.IntegerField(blank=True, null=True)#Posible enlace cambiar nombre codcentrotrabajo y enlace a centros trabajo 
    tarifaarl = models.CharField(max_length=10, blank=True, null=True) #quitar 
    ciudadcontratacion = models.CharField(max_length=40, blank=True, null=True)# enlace Ciudad 
    fondocesantias = models.CharField(max_length=80, blank=True, null=True)# enlace segsocial
    estadocontrato = models.SmallIntegerField(blank=True, null=True)# choice de estados 
    salario = models.IntegerField(blank=True, null=True) 
    idempleado = models.ForeignKey('Contratosemp', models.DO_NOTHING, db_column='idempleado', blank=True, null=True) 
    tipocotizante = models.CharField(max_length=120, blank=True, null=True) #enlace tiposdecotizantes
    subtipocotizante = models.CharField(max_length=120, blank=True, null=True)#enlace subtipocotizantes
    formapago = models.CharField(max_length=25, blank=True, null=True)#Choice 
    metodoretefuente = models.CharField(max_length=25, blank=True, null=True) #choice - formula o  calculo por año
    porcentajeretefuente = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)#manualmente 
    valordeduciblevivienda = models.IntegerField(blank=True, null=True)#manualmente 
    saludretefuente = models.IntegerField(blank=True, null=True)#manualmente 
    pensionado = models.CharField(max_length=25, blank=True, null=True)#boleano 
    estadoliquidacion = models.SmallIntegerField(blank=True, null=True)#choice Estadoliquidacion  
    estadosegsocial = models.SmallIntegerField(blank=True, null=True)#choice Estadosegsocial 
    motivoretiro = models.CharField(max_length=25, blank=True, null=True)#unificar con choice 
    tiposalario = models.SmallIntegerField(blank=True, null=True)#Posible choice
    idcontrato = models.AutoField(primary_key=True) 
    idcosto = models.ForeignKey('Costos', models.DO_NOTHING, db_column='idcosto', blank=True, null=True)
    idsubcosto = models.SmallIntegerField(blank=True, null=True)#Posible enlace 
    idsede = models.ForeignKey('Sedes', models.DO_NOTHING, db_column='idsede', blank=True, null=True) 
    salariovariable = models.SmallIntegerField(blank=True, null=True)#boleano 
    codeps = models.CharField(max_length=8, blank=True, null=True)#enlace segsocial
    codafp = models.CharField(max_length=8, blank=True, null=True)#enlace segsocial
    codccf = models.CharField(max_length=8, blank=True, null=True)#enlace segsocial
    auxiliotransporte = models.SmallIntegerField(blank=True, null=True)#boleano 
    dependientes = models.SmallIntegerField(blank=True, null=True)#manualmente 
    valordeduciblemedicina = models.IntegerField(blank=True, null=True)#manualmente 
    jornada = models.CharField(blank=True, null=True)#choice
    idmodelo = models.SmallIntegerField(blank=True, null=True)#enlace modelos_contratos
    coddepartamento = models.CharField(max_length=2, blank=True, null=True)##quitar 
    codciudad = models.CharField(max_length=3, blank=True, null=True)##quitar 
    riesgo_pension = models.CharField(max_length=5, blank=True, null=True)#boleano 

    class Meta:
        managed = False
        db_table = 'contratos'


class ContratosImportador(models.Model):
    idcontrato = models.SmallIntegerField(primary_key=True)
    novedad1 = models.CharField(max_length=255, blank=True, null=True)
    novedad2 = models.CharField(max_length=255, blank=True, null=True)
    novedad3 = models.CharField(max_length=255, blank=True, null=True)
    novedad4 = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contratos_importador'


class Contratosemp(models.Model):
    docidentidad = models.BigIntegerField(unique=True)
    tipodocident = models.CharField(max_length=20, blank=True, null=True)#Posible enlace 
    pnombre = models.CharField(max_length=50, blank=True, null=True)
    snombre = models.CharField(max_length=50, blank=True, null=True)
    papellido = models.CharField(max_length=50, blank=True, null=True)
    sapellido = models.CharField(max_length=50, blank=True, null=True)
    fechanac = models.DateField(blank=True, null=True)
    ciudadnacimiento = models.TextField(blank=True, null=True)#Posible enlace 
    telefonoempleado = models.CharField(max_length=12, blank=True, null=True)
    direccionempleado = models.CharField(max_length=100, blank=True, null=True)
    fotografiaempleado = models.CharField(blank=True, null=True)
    sexo = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    ciudadresidencia = models.CharField(max_length=20, blank=True, null=True)
    estadocivil = models.CharField(max_length=20, blank=True, null=True)
    idempleado = models.AutoField(primary_key=True)
    paisnacimiento = models.CharField(max_length=40, blank=True, null=True)
    paisresidencia = models.CharField(max_length=40, blank=True, null=True)
    celular = models.CharField(max_length=12, blank=True, null=True)
    profesion = models.CharField(max_length=180, blank=True, null=True)
    niveleducativo = models.CharField(max_length=25, blank=True, null=True)
    gruposanguineo = models.CharField(max_length=10, blank=True, null=True)
    estatura = models.CharField(max_length=10, blank=True, null=True)
    peso = models.CharField(max_length=10, blank=True, null=True)
    fechaexpedicion = models.DateField(blank=True, null=True)
    ciudadexpedicion = models.CharField(max_length=20, blank=True, null=True)
    dotpantalon = models.CharField(max_length=10, blank=True, null=True)
    dotcamisa = models.CharField(max_length=10, blank=True, null=True)
    dotzapatos = models.CharField(max_length=10, blank=True, null=True)
    estrato = models.CharField(max_length=5, blank=True, null=True)
    numlibretamil = models.CharField(max_length=10, blank=True, null=True)
    estadocontrato = models.SmallIntegerField(blank=True, null=True)
    formatohv = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contratosemp'


class Costos(models.Model):
    """
    tabla Costos 
    idempresa 
    usar donde requiera 
    """
    nomcosto = models.CharField(max_length=30, blank=True, null=True)
    idcosto = models.SmallAutoField(primary_key=True)#models.AutoField(primary_key=True) 
    grupocontable = models.CharField(max_length=4, blank=True, null=True)
    suficosto = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'costos'


class Crearnomina(models.Model):
    """
    tabla Crearnomina 
    idempresa 
    usar donde requiera 
    """
    nombrenomina = models.CharField(max_length=40, blank=True, null=True)## tipo ( liquidacion o nomina ) mes  - año = nomina - enero - 2024 - 1 o 2
    fechainicial = models.DateField(blank=True, null=True)
    fechafinal = models.DateField(blank=True, null=True)
    fechapago = models.DateField(blank=True, null=True)
    tipodenomina = models.CharField(max_length=2, blank=True, null=True) # enlace tipodenomina 
    mesacumular = models.CharField(max_length=20, blank=True, null=True) # estandar mayusculas 
    anoacumular = models.CharField(max_length=4, blank=True, null=True) # año 
    estadonomina = models.SmallIntegerField(blank=True, null=True)# boleano 
    diasnomina = models.SmallIntegerField(blank=True, null=True)#calculado
    idnomina = models.IntegerField(primary_key=True)#models.AutoField(primary_key=True) 
    mensaje = models.CharField(max_length=255, blank=True, null=True)#quitar
    finicialextras = models.DateField(blank=True, null=True)#quitar
    ffinalextras = models.DateField(blank=True, null=True)#quitar
    totalempleados = models.SmallIntegerField(blank=True, null=True)#quitar
    totalincapacitados = models.SmallIntegerField(blank=True, null=True)#quitar
    totalenvacaciones = models.SmallIntegerField(blank=True, null=True)#quitar
    totalporliquidar = models.SmallIntegerField(blank=True, null=True)#quitar

    class Meta:
        managed = False
        db_table = 'crearnomina'


class Diagnosticosenfermedades(models.Model):
    """
    tabla Diagnosticosenfermedades 
    comun a todos 
    """
    coddiagnostico = models.CharField(primary_key=True, max_length=255)
    diagnostico = models.CharField(max_length=255, blank=True, null=True)
    prefijo = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'diagnosticosenfermedades'


class DocCategorias(models.Model):
    """
    se deja igual 
    """
    idcat = models.IntegerField(primary_key=True)
    doc_categoria = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'doc_categorias'


class DocDocumentos(models.Model):
    """
    se deja igual 
    """
    iddoc = models.IntegerField(primary_key=True)
    tipo = models.CharField(blank=True, null=True)
    titulo = models.CharField(blank=True, null=True)
    idempleado = models.CharField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    usuario = models.CharField(blank=True, null=True)
    documento = models.BinaryField(blank=True, null=True)
    nomarchivo = models.CharField(blank=True, null=True)
    tamarchivo = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'doc_documentos'


class EmpVacaciones(models.Model):
    """
    tabla EmpVacaciones
    
    """
    id_sol_vac = models.AutoField(primary_key=True)#models.AutoField(primary_key=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING, db_column='idcontrato', blank=True, null=True)
    tipovac = models.ForeignKey('Tipoavacaus', models.DO_NOTHING, db_column='tipovac', blank=True, null=True)
    fechainicialvac = models.DateField(blank=True, null=True)
    fechafinalvac = models.DateField(blank=True, null=True)
    estado = models.SmallIntegerField(blank=True, null=True)
    diasvac = models.SmallIntegerField(blank=True, null=True)
    cuentasabados = models.SmallIntegerField(blank=True, null=True)
    diascalendario = models.SmallIntegerField(blank=True, null=True)
    idempleado = models.ForeignKey(Contratosemp, models.DO_NOTHING, db_column='idempleado', blank=True, null=True)#quitar 
    ip_usuario = models.CharField(max_length=16, blank=True, null=True)
    fecha_hora = models.DateTimeField(blank=True, null=True)
    ## 
    update = models.DateTimeField(blank=True, null=True)# quitar 
    comentarios = models.CharField(max_length=255, blank=True, null=True)
    comentarios2 = models.CharField(max_length=255, blank=True, null=True)
    update_ip = models.CharField(max_length=16, blank=True, null=True) # quitar 

    class Meta:
        managed = False
        db_table = 'emp_vacaciones'


class Empresa(models.Model):
    idempresa = models.CharField(primary_key=True, max_length=10)
    nit = models.CharField(max_length=20)
    nombreempresa = models.CharField(max_length=255, blank=True, null=True)
    direccionempresa = models.CharField(max_length=255, blank=True, null=True)
    replegal = models.CharField(max_length=255, blank=True, null=True)
    arl = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=40, blank=True, null=True)
    ciudad = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=30, blank=True, null=True)
    codarl = models.CharField(max_length=15, blank=True, null=True)
    idcliente = models.SmallIntegerField(blank=True, null=True)
    bdatos = models.CharField(max_length=20, blank=True, null=True)
    contactonomina = models.CharField(max_length=50, blank=True, null=True)
    emailnomina = models.CharField(max_length=50, blank=True, null=True)
    contactorrhh = models.CharField(max_length=50, blank=True, null=True)
    emailrrhh = models.CharField(max_length=50, blank=True, null=True)
    contactocontab = models.CharField(max_length=50, blank=True, null=True)
    emailcontab = models.CharField(max_length=50, blank=True, null=True)
    cargocertificaciones = models.CharField(max_length=50, blank=True, null=True)
    firmacertificaciones = models.CharField(max_length=50, blank=True, null=True)
    website = models.CharField(blank=True, null=True)
    metodoextras = models.CharField(blank=True, null=True)
    dv = models.CharField(blank=True, null=True)
    coddpto = models.CharField(blank=True, null=True)
    codciudad = models.CharField(blank=True, null=True)
    nomciudad = models.CharField(blank=True, null=True)
    ajustarnovedad = models.CharField(max_length=2, blank=True, null=True)
    realizarparafiscales = models.CharField(max_length=2, blank=True, null=True)
    vstccf = models.CharField(max_length=2, blank=True, null=True)
    vstsenaicbf = models.CharField(max_length=2, blank=True, null=True)
    ige100 = models.CharField(max_length=2, blank=True, null=True)
    slntarifapension = models.CharField(max_length=2, blank=True, null=True)
    tipodoc = models.CharField(max_length=2, blank=True, null=True)
    codigosuc = models.CharField(max_length=10, blank=True, null=True)
    nombresuc = models.CharField(max_length=40, blank=True, null=True)
    claseaportante = models.CharField(max_length=1, blank=True, null=True)
    tipoaportante = models.SmallIntegerField(blank=True, null=True)
    banco = models.CharField(max_length=3, blank=True, null=True)
    numcuenta = models.CharField(max_length=255, blank=True, null=True)
    tipocuenta = models.CharField(max_length=10, blank=True, null=True)
    pais = models.CharField(max_length=80, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empresa'


class Entidadessegsocial(models.Model):
    """
    comun todos 
    """
    codigo = models.CharField(primary_key=True, max_length=9)
    nit = models.CharField(max_length=12)
    entidad = models.CharField(max_length=120)
    tipoentidad = models.CharField(max_length=20)
    codsgp = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entidadessegsocial'


class EstActivos(models.Model):
    """
    se deja igual 
    """
    idmes = models.SmallIntegerField(primary_key=True)
    mes = models.CharField(max_length=255, blank=True, null=True)
    ano = models.IntegerField(blank=True, null=True)
    empleados = models.SmallIntegerField(blank=True, null=True)
    devengados = models.IntegerField(blank=True, null=True)
    extras = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'est_activos'


class Estaturas(models.Model):
    """
    quitar 
    """
    idestatura = models.SmallIntegerField(primary_key=True)
    estatura = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estaturas'


class Festivos(models.Model):
    """
    festivos : añadir automatizacion 
    """
    idfestivo = models.IntegerField(primary_key=True)
    dia = models.DateField(blank=True, null=True)
    descripcion = models.CharField(max_length=60, blank=True, null=True)
    ano = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'festivos'


class Incapacidades(models.Model):
    """
    
    """
    idincapacidad = models.IntegerField(primary_key=True)#models.AutoField(primary_key=True)
    empleado = models.CharField(max_length=80, blank=True, null=True)# quitar 
    certificadoincapacidad = models.CharField(max_length=15, blank=True, null=True)
    tipoentidad = models.CharField(max_length=5, blank=True, null=True)# EPS O ARL quitar 
    entidad = models.CharField(max_length=80, blank=True, null=True) #enlace segsocial
    coddiagnostico = models.CharField(max_length=15, blank=True, null=True)#enlace diasnostico  
    diagnostico = models.CharField(max_length=255, blank=True, null=True)#quitar
    fechainicial = models.DateField(blank=True, null=True)
    dias = models.IntegerField(blank=True, null=True)
    nominaincap = models.CharField(max_length=30, blank=True, null=True)# quitar 
    imagenincapacidad = models.CharField(blank=True, null=True) # cambiar tipo enlace 
    idempleado = models.IntegerField(blank=True, null=True) # quitar
    idcontrato = models.IntegerField(blank=True, null=True) # fk a contratos y fk principal 
    estadonovincap = models.SmallIntegerField(blank=True, null=True) #quitar 
    prorroga = models.CharField(max_length=5, blank=True, null=True) #boleano 
    ibc = models.IntegerField(blank=True, null=True)# calculado 
    saldodias = models.SmallIntegerField(blank=True, null=True) # quitar 
    origenincap = models.CharField(blank=True, null=True) # choice 
    finincap = models.DateField(blank=True, null=True) #quitar  
    imagenblob = models.BinaryField(blank=True, null=True)# quitar 
    liq = models.CharField(max_length=255, blank=True, null=True) # quitar 
    prefijo = models.CharField(max_length=7, blank=True, null=True) # quitar 

    class Meta:
        managed = False
        db_table = 'incapacidades'


class IncapacidadesAmor(models.Model):
    """
    eliminar 
    """
    idincapacidad = models.IntegerField(blank=True, null=True)
    fechainicial = models.DateField(blank=True, null=True)
    idcontrato = models.IntegerField(blank=True, null=True)
    idempleado = models.IntegerField(blank=True, null=True)
    diasenmes = models.SmallIntegerField(blank=True, null=True)
    mesacumular = models.CharField(blank=True, null=True)
    anoacumular = models.CharField(blank=True, null=True)
    ibc = models.IntegerField(blank=True, null=True)
    saldodias = models.SmallIntegerField(blank=True, null=True)
    idregincap = models.IntegerField(primary_key=True)
    prorroga = models.CharField(max_length=2, blank=True, null=True)
    origenincap = models.CharField(blank=True, null=True)
    finincap = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'incapacidades_amor'


class IncapacidadesImportador(models.Model):
    
    """
    igual a Incapacidades mejora de incapacidades 
    """
    
    cedula = models.IntegerField(blank=True, null=True)
    tipoentidad = models.CharField(blank=True, null=True)
    entidad = models.CharField(blank=True, null=True)
    origenincapacidad = models.CharField(blank=True, null=True)
    prefijo = models.CharField(max_length=1, blank=True, null=True)
    coddiagnostico = models.CharField(blank=True, null=True)
    prorroga = models.CharField(blank=True, null=True)
    dias = models.IntegerField(blank=True, null=True)
    diagnostico = models.CharField(blank=True, null=True)
    idnomina = models.IntegerField(blank=True, null=True)
    fechainicial = models.DateField(blank=True, null=True)
    fechafinal = models.DateField(blank=True, null=True)
    idcontrato = models.IntegerField(blank=True, null=True)
    idempleado = models.IntegerField(blank=True, null=True)
    ibc = models.IntegerField(blank=True, null=True)
    nombreemp = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'incapacidades_importador'


class Ingresosyretenciones(models.Model):
    """
    
    
    """
    idingret = models.SmallIntegerField(primary_key=True) #models.AutoField(primary_key=True)
    tipodocumento = models.CharField(blank=True, null=True)#quitar 
    docidentidad = models.CharField(blank=True, null=True)#quitar
    papellido = models.CharField(blank=True, null=True)#quitar
    sapellido = models.CharField(blank=True, null=True)#quitar
    pnombre = models.CharField(blank=True, null=True)#quitar
    snombre = models.CharField(blank=True, null=True)#quitar
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
    anoacumular = models.CharField(blank=True, null=True)
    idempleado = models.IntegerField(blank=True, null=True)#enlace principal 
    otrospagos = models.IntegerField(blank=True, null=True)
    fondocesantias = models.IntegerField(blank=True, null=True)
    excesoalim = models.IntegerField(blank=True, null=True)
    cesantias90 = models.IntegerField(blank=True, null=True)
    apoyoeconomico = models.IntegerField(blank=True, null=True)
    aportesavc = models.IntegerField(blank=True, null=True)
    ingresolaboralpromedio = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ingresosyretenciones'


class Jornadas(models.Model):
    """
    dejar por ahora , posible analisis 
    """
    idjornada = models.SmallIntegerField()
    jornada = models.CharField(max_length=40, blank=True, null=True)
    extras = models.CharField(blank=True, null=True)
    lunes1 = models.CharField(blank=True, null=True)
    lunes2 = models.CharField(blank=True, null=True)
    martes1 = models.CharField(blank=True, null=True)
    martes2 = models.CharField(blank=True, null=True)
    miercoles1 = models.CharField(blank=True, null=True)
    miercoles2 = models.CharField(blank=True, null=True)
    jueves1 = models.CharField(blank=True, null=True)
    jueves2 = models.CharField(blank=True, null=True)
    viernes1 = models.CharField(blank=True, null=True)
    viernes2 = models.CharField(blank=True, null=True)
    sabado1 = models.CharField(blank=True, null=True)
    sabado2 = models.CharField(blank=True, null=True)
    domingo1 = models.CharField(blank=True, null=True)
    domingo2 = models.CharField(blank=True, null=True)
    horareceso = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jornadas'


class Liquidacion(models.Model):
    """
    
    """
    idliquidacion = models.IntegerField(primary_key=True) #models.AutoField(primary_key=True)
    docidentidad = models.CharField(max_length=15, blank=True, null=True)#quitar
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
    idcontrato = models.IntegerField()#fk principal 
    idempleado = models.IntegerField(blank=True, null=True)#quitar 
    fechainiciocontrato = models.DateField(blank=True, null=True)
    fechafincontrato = models.DateField(blank=True, null=True)
    salario = models.IntegerField(blank=True, null=True)
    motivoretiro = models.CharField(blank=True, null=True)# choice 
    estadoliquidacion = models.CharField(blank=True, null=True)# boleano 
    diassusp = models.SmallIntegerField(blank=True, null=True)
    indemnizacion = models.IntegerField(blank=True, null=True)
    diassuspv = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'liquidacion'
        unique_together = (('idliquidacion', 'idcontrato'),)


class LiquidacionMasivo(models.Model):
    """
    estructura igual Liquidacion
    """
    idliquidacion = models.IntegerField(primary_key=True) 
    docidentidad = models.CharField(max_length=15, blank=True, null=True)
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
    idcontrato = models.IntegerField()
    idempleado = models.IntegerField(blank=True, null=True)
    fechainiciocontrato = models.DateField(blank=True, null=True)
    fechafincontrato = models.DateField(blank=True, null=True)
    salario = models.IntegerField(blank=True, null=True)
    motivoretiro = models.CharField(blank=True, null=True)
    estadoliquidacion = models.CharField(blank=True, null=True)
    diassusp = models.SmallIntegerField(blank=True, null=True)
    indemnizacion = models.IntegerField(blank=True, null=True)
    diassuspv = models.CharField(max_length=16, blank=True, null=True)
    idcosto = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'liquidacion_masivo'
        unique_together = (('idliquidacion', 'idcontrato'),)


class Mediospago(models.Model):
    """
    medios de pago - validar con fer 
    """
    cod_dian = models.SmallIntegerField(blank=True, null=True)
    medio = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mediospago'


class Meses(models.Model):
    """
    choice quitar 
    """
    mes = models.CharField(max_length=30, blank=True, null=True)
    idmes = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'meses'


class ModelosContratos(models.Model):
    """
    dejar quieta 
    """
    idmodelo = models.SmallIntegerField(primary_key=True)
    nombremodelo = models.CharField(max_length=255, blank=True, null=True)
    tipocontrato = models.CharField(max_length=255, blank=True, null=True)
    textocontrato = models.CharField(max_length=10485760, blank=True, null=True)
    estadomodelo = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'modelos_contratos'


class NeDatosMensual(models.Model):
    idnominaelectronica = models.SmallIntegerField(primary_key=True)
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
        managed = False
        db_table = 'ne_datos_mensual'


class NeDetalleNominaElectronica(models.Model):
    id_detalle_nomina_electronica = models.IntegerField(primary_key=True)
    id_ne_datos_mensual = models.ForeignKey(NeDatosMensual, models.DO_NOTHING, db_column='id_ne_datos_mensual', blank=True, null=True)
    id_contrato = models.IntegerField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_modificacion = models.DateTimeField(blank=True, null=True)
    json_nomina = models.TextField(blank=True, null=True)
    estado = models.IntegerField(blank=True, null=True)
    tipo_registro = models.IntegerField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ne_detalle_nomina_electronica'


class NeRespuestaDian(models.Model):
    id_ne_respuesta_dian = models.AutoField(primary_key=True)
    id_ne_detalle_nomina_electronica = models.ForeignKey(NeDetalleNominaElectronica, models.DO_NOTHING, db_column='id_ne_detalle_nomina_electronica', blank=True, null=True)
    fecha_transaccion = models.DateTimeField(blank=True, null=True)
    json_respuesta = models.TextField(blank=True, null=True)
    codigo_respuesta = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ne_respuesta_dian'


class NeSumatorias(models.Model):
    ne_id = models.CharField(primary_key=True, max_length=8)
    campo = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ne_sumatorias'


class Nivelesestructura(models.Model):
    idnivel = models.SmallIntegerField(primary_key=True)
    nombrenivel = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nivelesestructura'


class Nomina(models.Model):
    """
    
    """
    idregistronom = models.IntegerField(primary_key=True) ##models.AutoField(primary_key=True)
    nombreconcepto = models.CharField(max_length=255, blank=True, null=True) #quitar 
    valor = models.IntegerField(blank=True, null=True)
    mesacumular = models.CharField(max_length=15, blank=True, null=True)#quitar
    anoacumular = models.CharField(max_length=15, blank=True, null=True)#quitar  
    idempleado = models.ForeignKey(Contratosemp, models.DO_NOTHING, db_column='idempleado', blank=True, null=True)#quitar 
    cantidad = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    idconcepto = models.ForeignKey(Conceptosdenomina, models.DO_NOTHING, db_column='idconcepto', blank=True, null=True)# fk principal
    idnomina = models.IntegerField(blank=True, null=True) # enlace a crear nomina 
    estadonomina = models.SmallIntegerField(blank=True, null=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING, db_column='idcontrato', blank=True, null=True)
    idcosto = models.ForeignKey(Costos, models.DO_NOTHING, db_column='idcosto', blank=True, null=True)
    idsubcosto = models.ForeignKey('Subcostos', models.DO_NOTHING, db_column='idsubcosto', blank=True, null=True)
    control = models.IntegerField(blank=True, null=True) # vacaciones o incapacidades o prestamos automatico  

    class Meta:
        managed = False
        db_table = 'nomina'


class NominaComprobantes(models.Model):
    """
    historico de nomina 
    otro planteamento 
    """
    idhistorico = models.AutoField(primary_key=True)
    idcontrato = models.IntegerField(blank=True, null=True) # enlace a contrato 
    salario = models.IntegerField(blank=True, null=True)
    cargo = models.CharField(max_length=120, blank=True, null=True)
    idcosto = models.SmallIntegerField(blank=True, null=True)# enlace a costos 
    pension = models.CharField(max_length=125, blank=True, null=True)
    salud = models.CharField(max_length=125, blank=True, null=True) 
    idnomina = models.IntegerField(blank=True, null=True) 
    envio_email = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nomina_comprobantes'


class NominaFija(models.Model):
    """
    quieta y se valida si se usa o no 
    
    """
    idregistronom = models.IntegerField(primary_key=True)
    idnomina = models.CharField(max_length=255, blank=True, null=True)# enlace a nomina 
    nombreconcepto = models.CharField(max_length=255, blank=True, null=True)
    valor = models.DecimalField(max_digits=11, decimal_places=1, blank=True, null=True)
    mesacumular = models.CharField(max_length=15, blank=True, null=True)# qui
    anoacumular = models.CharField(max_length=15, blank=True, null=True)#
    multiplicadorconcepto = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    cantidad = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    idconcepto = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nomina_fija'


class NominaImportador(models.Model):
    """
    igualar a nomina 
    """
    id_reg = models.BigAutoField(primary_key=True)
    idnomina = models.IntegerField(blank=True, null=True)
    idconcepto = models.SmallIntegerField(blank=True, null=True)
    cantidad = models.IntegerField(blank=True, null=True)
    valor = models.BigIntegerField(blank=True, null=True)
    idcontrato = models.IntegerField(blank=True, null=True)
    docidentidad = models.IntegerField(blank=True, null=True)
    idcosto = models.SmallIntegerField(blank=True, null=True)
    idsubcosto = models.SmallIntegerField(blank=True, null=True)
    nombreconcepto = models.CharField(max_length=60, blank=True, null=True)
    mesacumular = models.CharField(max_length=40, blank=True, null=True)
    anoacumular = models.CharField(max_length=4, blank=True, null=True)
    idempleado = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nomina_importador'


class NovCambiocargo(models.Model):
    """
    igual 
    """
    idcambiocargo = models.IntegerField(primary_key=True)
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
        managed = False
        db_table = 'nov_cambiocargo'


class NovDescuentos(models.Model):
    """
    igual 
    """
    idnovdescuento = models.IntegerField(primary_key=True)
    idempleado = models.IntegerField(blank=True, null=True)
    idcontrato = models.IntegerField(blank=True, null=True)
    empleado = models.CharField(max_length=50, blank=True, null=True)
    conceptodescuento = models.CharField(max_length=50, blank=True, null=True)
    valordescuento = models.IntegerField(blank=True, null=True)
    fechanovedad = models.DateField(blank=True, null=True)
    idnomina = models.IntegerField(blank=True, null=True)
    estadonovdes = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nov_descuentos'


class NovFijos(models.Model):
    """
    
    """
    idnovfija = models.IntegerField(primary_key=True)
    idconcepto = models.IntegerField(blank=True, null=True)#enlace
    nombreconcepto = models.CharField(max_length=255, blank=True, null=True)#quitar
    valor = models.IntegerField(blank=True, null=True)
    idcontrato = models.IntegerField(blank=True, null=True)#fk principal 
    idempleado = models.IntegerField(blank=True, null=True)#quitar
    estado_novfija = models.CharField(max_length=8, blank=True, null=True)#boleano 
    pago = models.CharField(max_length=40, blank=True, null=True)
    diapago = models.SmallIntegerField(blank=True, null=True)
    descripcion = models.CharField(max_length=40, blank=True, null=True)
    fechafinnovedad = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nov_fijos'


class NovSalarios(models.Model):
    """
    
    """
    idcambiosalario = models.IntegerField(primary_key=True)
    idcontrato = models.IntegerField(blank=True, null=True)#fk principal 
    idempleado = models.IntegerField(blank=True, null=True)#quitat
    salarioactual = models.IntegerField(blank=True, null=True)# automatico 
    nuevosalario = models.IntegerField(blank=True, null=True)#manual 
    fechanuevosalario = models.DateField(blank=True, null=True)
    aprobarcs = models.CharField(max_length=1, blank=True, null=True)#quitat
    empleado = models.CharField(max_length=40, blank=True, null=True)#quitat
    estadonovsal = models.SmallIntegerField(blank=True, null=True)#quitat
    tiposalario = models.SmallIntegerField(blank=True, null=True)#enlace tiposalarios 

    class Meta:
        managed = False
        db_table = 'nov_salarios'


class NovSegsocial(models.Model):
    """
    validar cambio de eps o pension modificar 
    
    """
    idcambiosegsocial = models.IntegerField(primary_key=True)
    idempleado = models.IntegerField(blank=True, null=True)#quitar
    idcontrato = models.IntegerField(blank=True, null=True)#fk principal 
    empleado = models.CharField(max_length=50, blank=True, null=True) # quitar 
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
        managed = False
        db_table = 'nov_segsocial'


class Paises(models.Model):
    """
    igual
    """
    idpais = models.SmallIntegerField(primary_key=True)
    pais = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'paises'


class Pila(models.Model):
    """
    proixima a validar informacion de pila 
    """
    idaportes = models.IntegerField(primary_key=True) 
    docidentidad = models.BigIntegerField()
    salario = models.CharField(max_length=8, blank=True, null=True)
    mesacumular = models.CharField(max_length=15, blank=True, null=True)
    anoacumular = models.CharField(max_length=15, blank=True, null=True)
    basesegsocial = models.IntegerField(blank=True, null=True)
    diaseps = models.CharField(max_length=6, blank=True, null=True)
    diasafp = models.IntegerField(blank=True, null=True)
    diasarl = models.IntegerField(blank=True, null=True)
    diasccf = models.IntegerField(blank=True, null=True)
    diasincapeps = models.IntegerField(blank=True, null=True)
    diasincaparl = models.IntegerField(blank=True, null=True)
    numautincapeps = models.IntegerField(blank=True, null=True)
    valincapeps = models.IntegerField(blank=True, null=True)
    diaslicmat = models.IntegerField(blank=True, null=True)
    numautlicmat = models.IntegerField(blank=True, null=True)
    vallicmat = models.IntegerField(blank=True, null=True)
    valeps = models.IntegerField(blank=True, null=True)
    valafp = models.IntegerField(blank=True, null=True)
    valarl = models.IntegerField(blank=True, null=True)
    valccf = models.IntegerField(blank=True, null=True)
    valicbf = models.IntegerField(blank=True, null=True)
    valsena = models.IntegerField(blank=True, null=True)
    tareps = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    tarifaarl = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    tarafp = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    tarccf = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    tarsena = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    taricbf = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    eps = models.CharField(max_length=50, blank=True, null=True)
    pension = models.CharField(max_length=50, blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pila'
        unique_together = (('idaportes', 'docidentidad'),)


class PilaConceptos(models.Model):
    """
    proixima a validar informacion de pila 
    """
    idnov = models.CharField(max_length=6)
    nombre_novedad = models.CharField(max_length=70, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pila_conceptos'


class PilaContenedor(models.Model):
    """
    proixima a validar informacion de pila 
    """
    id_pila_contenedor = models.AutoField(primary_key=True)
    estado = models.IntegerField()
    mes = models.CharField()
    anio = models.CharField()
    fecha_pago = models.DateField(blank=True, null=True)
    archivo_generado = models.CharField(blank=True, null=True)
    tamanio_archivo = models.CharField(blank=True, null=True)
    fecha_generacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pila_contenedor'


class PilaEstado(models.Model):
    """
    proixima a validar informacion de pila 
    """
    id_pila_estado = models.AutoField(primary_key=True)
    nombre_estado_pila = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'pila_estado'


class PilaFijos(models.Model):
    """
    proixima a validar informacion de pila 
    """
    idfix = models.BigAutoField()
    docidentidad = models.CharField(max_length=40, blank=True, null=True)
    idcontrato = models.CharField(max_length=7, blank=True, null=True)
    diaspension = models.SmallIntegerField(blank=True, null=True)
    diassalud = models.SmallIntegerField(blank=True, null=True)
    diasarl = models.SmallIntegerField(blank=True, null=True)
    diasccf = models.SmallIntegerField(blank=True, null=True)
    salariobasico = models.SmallIntegerField(blank=True, null=True)
    ibcpension = models.SmallIntegerField(blank=True, null=True)
    ibcsalud = models.SmallIntegerField(blank=True, null=True)
    ibcarl = models.SmallIntegerField(blank=True, null=True)
    ibcccf = models.SmallIntegerField(blank=True, null=True)
    tarpen = models.SmallIntegerField(blank=True, null=True)
    cotpen = models.SmallIntegerField(blank=True, null=True)
    apvolpen = models.SmallIntegerField(blank=True, null=True)
    apvolpenemp = models.SmallIntegerField(blank=True, null=True)
    totalcotpen = models.SmallIntegerField(blank=True, null=True)
    fsp = models.SmallIntegerField(blank=True, null=True)
    fspsub = models.SmallIntegerField(blank=True, null=True)
    noretapvol = models.SmallIntegerField(blank=True, null=True)
    tarsalud = models.SmallIntegerField(blank=True, null=True)
    cotsalud = models.SmallIntegerField(blank=True, null=True)
    upc = models.SmallIntegerField(blank=True, null=True)
    tararl = models.SmallIntegerField(blank=True, null=True)
    centrotrabajo = models.SmallIntegerField(blank=True, null=True)
    cotarl = models.SmallIntegerField(blank=True, null=True)
    tarccf = models.SmallIntegerField(blank=True, null=True)
    apccf = models.SmallIntegerField(blank=True, null=True)
    tarsena = models.SmallIntegerField(blank=True, null=True)
    apsena = models.SmallIntegerField(blank=True, null=True)
    taricbf = models.SmallIntegerField(blank=True, null=True)
    apicbf = models.SmallIntegerField(blank=True, null=True)
    taresap = models.SmallIntegerField(blank=True, null=True)
    apesap = models.SmallIntegerField(blank=True, null=True)
    tarmen = models.SmallIntegerField(blank=True, null=True)
    apmen = models.SmallIntegerField(blank=True, null=True)
    ley1607 = models.CharField(max_length=1, blank=True, null=True)
    mesacumular = models.CharField(max_length=10, blank=True, null=True)
    anoacumular = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pila_fijos'


class PilaNovedades(models.Model):
    
    """
    proixima a validar informacion de pila 
    """
    idnov = models.AutoField()
    docidentidad = models.IntegerField(blank=True, null=True)
    idcontrato = models.IntegerField(blank=True, null=True)
    mesacumular = models.CharField(max_length=20, blank=True, null=True)
    anoacumular = models.CharField(max_length=8, blank=True, null=True)
    tiponovedad = models.CharField(max_length=10, blank=True, null=True)
    valortotal = models.IntegerField(blank=True, null=True)
    ajustarnovedad = models.CharField(max_length=2, blank=True, null=True)
    realizarparafiscales = models.CharField(max_length=2, blank=True, null=True)
    diainicial = models.SmallIntegerField(blank=True, null=True)
    diaduracion = models.SmallIntegerField(blank=True, null=True)
    tipoingresoretiro = models.SmallIntegerField(blank=True, null=True)
    vstccf = models.CharField(max_length=2, blank=True, null=True)
    vstsenaicbf = models.CharField(max_length=2, blank=True, null=True)
    ige100 = models.CharField(max_length=16, blank=True, null=True)
    slntipo = models.CharField(max_length=30, blank=True, null=True)
    slntarifapension = models.CharField(max_length=30, blank=True, null=True)
    vactipo = models.CharField(max_length=30, blank=True, null=True)
    vhl = models.SmallIntegerField(blank=True, null=True)
    tipoid = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pila_novedades'


class Prestamos(models.Model):
    idprestamo = models.SmallIntegerField(primary_key=True)
    idempleado = models.SmallIntegerField(blank=True, null=True)# quitar
    idcontrato = models.SmallIntegerField(blank=True, null=True)# fk principal 
    valorprestamo = models.IntegerField(blank=True, null=True) 
    fechaprestamo = models.DateField(blank=True, null=True)
    cuotasprestamo = models.SmallIntegerField(blank=True, null=True)
    valorcuota = models.IntegerField(blank=True, null=True)
    saldoprestamo = models.IntegerField(blank=True, null=True) #quitar 
    cuotaspagadas = models.SmallIntegerField(blank=True, null=True) #quitar 
    empleado = models.CharField(max_length=40, blank=True, null=True)# quitar 
    estadoprestamo = models.SmallIntegerField(blank=True, null=True)#boleano
    formapago = models.SmallIntegerField(blank=True, null=True) # quitar
    diapago = models.SmallIntegerField(blank=True, null=True)#quitar 

    class Meta:
        managed = False
        db_table = 'prestamos'


class PrestamosAmor(models.Model):
    #quitar tabla completa
    idprestamo = models.SmallIntegerField(blank=True, null=True)
    idempleado = models.SmallIntegerField(blank=True, null=True)
    idcontrato = models.SmallIntegerField(blank=True, null=True)
    valorcuota = models.IntegerField(blank=True, null=True)
    estadocuota = models.SmallIntegerField(blank=True, null=True)
    diapago = models.SmallIntegerField(blank=True, null=True)
    pago = models.CharField(max_length=40, blank=True, null=True)
    estadoprestamo = models.SmallIntegerField(blank=True, null=True)
    idnomina = models.IntegerField(blank=True, null=True)
    numcuota = models.SmallIntegerField(blank=True, null=True)
    idregcuota = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'prestamos_amor'


class Profesiones(models.Model):
    #se deja igual 
    #comun todos 
    idprofesion = models.SmallIntegerField(primary_key=True)
    profesion = models.CharField(max_length=180, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'profesiones'


class ProvisionesContables(models.Model):
    """
    
    """
    idregistronom = models.IntegerField(primary_key=True)
    nombreconcepto = models.CharField(max_length=255, blank=True, null=True)#quitar 
    valor = models.IntegerField(blank=True, null=True)
    mesacumular = models.CharField(max_length=15, blank=True, null=True)
    anoacumular = models.CharField(max_length=15, blank=True, null=True)
    idconcepto = models.IntegerField(blank=True, null=True)#fk a conceptos 
    idcontrato = models.IntegerField(blank=True, null=True)#fkprincipal 
    idcosto = models.SmallIntegerField(blank=True, null=True)#fk a costos
    idnomina = models.IntegerField(blank=True, null=True)#quitar 
    entidad = models.CharField(max_length=32, blank=True, null=True) # nit 

    class Meta:
        managed = False
        db_table = 'provisiones_contables'


class Salariominimoanual(models.Model):
    #se deja igual 
    idano = models.SmallIntegerField(primary_key=True)
    salariominimo = models.IntegerField(blank=True, null=True)
    auxtransporte = models.IntegerField(blank=True, null=True)
    uvt = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'salariominimoanual'


class SalariosImportador(models.Model):
    """
    cambio masivo se valida mas adelante 
    """
    id_salario = models.BigAutoField(primary_key=True)
    docidentidad = models.IntegerField(blank=True, null=True)
    nuevosalario = models.IntegerField(blank=True, null=True)
    fechanuevosalario = models.DateField(blank=True, null=True)
    tiposalario = models.SmallIntegerField(blank=True, null=True)
    idcontrato = models.IntegerField(blank=True, null=True)
    idempleado = models.IntegerField(blank=True, null=True)
    salarioanterior = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'salarios_importador'


class ScLog(models.Model):
    ## logs geenrar con django elimiar tabla 
    inserted_date = models.DateTimeField(blank=True, null=True)
    username = models.CharField(max_length=90)
    application = models.CharField(max_length=200)
    creator = models.CharField(max_length=30)
    ip_user = models.CharField(max_length=32)
    action = models.CharField(max_length=30)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sc_log'


class Sedes(models.Model):
    # igual 
    nombresede = models.CharField(max_length=40, blank=True, null=True)
    cajacompensacion = models.CharField(max_length=60, blank=True, null=True)
    idsede = models.SmallAutoField(primary_key=True)
    codccf = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sedes'


class Subcostos(models.Model):
    #igual 
    nomsubcosto = models.CharField(max_length=30, blank=True, null=True)
    nomcosto = models.CharField(max_length=30, blank=True, null=True)#quitar
    idsubcosto = models.SmallIntegerField(primary_key=True)
    idcosto = models.SmallIntegerField(blank=True, null=True)#enlace a costos 
    sufisubcosto = models.CharField(max_length=2, blank=True, null=True) 

    class Meta:
        managed = False
        db_table = 'subcostos'


class Subtipocotizantes(models.Model):
    """ 
    igual 
    """
    subtipocotizante = models.CharField(primary_key=True, max_length=2)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    codplanilla = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subtipocotizantes'


class Tiempos(models.Model):
    """
    validar con aplicativo reloj 
    """
    idmarcacion = models.AutoField(primary_key=True)
    fechaingreso = models.DateField(blank=True, null=True)
    horaingreso = models.TimeField(blank=True, null=True)
    horasalida = models.TimeField(blank=True, null=True)
    horasdescuentos = models.TimeField(blank=True, null=True)
    idcontrato = models.IntegerField(blank=True, null=True)
    idnomina = models.IntegerField(blank=True, null=True)
    fechasalida = models.DateField(blank=True, null=True)
    horasord = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    horastrab = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    horasdomfes = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    hed = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    hen = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    hedf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    henf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    rn = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    rnf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    dyf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    sede = models.CharField(blank=True, null=True)
    fechaturno = models.DateField(blank=True, null=True)#quitar
    saldo = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)#quitar

    class Meta:
        managed = False
        db_table = 'tiempos'


class TiemposTotales(models.Model):
    idtiempostotales = models.IntegerField(primary_key=True)
    idcontrato = models.IntegerField(blank=True, null=True)#fk principal 
    horasord = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    horastrab = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    horasdomfes = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    hed = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    vhed = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    hen = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    vhen = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    hedf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    vhedf = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    henf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    vhenf = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rn = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    vrn = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rnf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    vrnf = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dyf = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    vdyf = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    idnomina = models.SmallIntegerField(blank=True, null=True)#enlace nomina 
    valorextras = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    empleado = models.CharField(max_length=60, blank=True, null=True)#quitar
    sede = models.CharField(max_length=60, blank=True, null=True)# enlace sede 
    saldo = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)#quitar 
    idcosto = models.CharField(max_length=3, blank=True, null=True)# enlace costo 
    idsubcosto = models.CharField(max_length=3, blank=True, null=True)# enlace subcosto

    class Meta:
        managed = False
        db_table = 'tiempos_totales'


class Tipoavacaus(models.Model):
    #dejar igual 
    tipovac = models.CharField(primary_key=True, max_length=255)
    nombrevacaus = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipoavacaus'


class Tipocontrato(models.Model):
    #igual 
    idtipocontrato = models.IntegerField(primary_key=True)
    tipocontrato = models.CharField(max_length=255, blank=True, null=True)
    cod_dian = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipocontrato'


class Tipodenomina(models.Model):
    #igual 
    idtiponomina = models.IntegerField(primary_key=True)
    tipodenomina = models.CharField(max_length=255)
    cod_dian = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipodenomina'


class Tipodocumento(models.Model):
    #igual 
    id_tipo_doc = models.SmallIntegerField(primary_key=True)
    documento = models.CharField(max_length=50, blank=True, null=True)
    codigo = models.CharField(max_length=4, blank=True, null=True)
    cod_dian = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipodocumento'


class Tiposalario(models.Model):
    #igual 
    idtiposalario = models.SmallIntegerField(primary_key=True)
    tiposalario = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tiposalario'


class Tiposdecotizantes(models.Model):
    #igual 
    tipocotizante = models.CharField(primary_key=True, max_length=2)
    descripcioncot = models.CharField(max_length=120, blank=True, null=True)
    codplanilla = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tiposdecotizantes'


class Vacaciones(models.Model):
    # 
    idempleado = models.SmallIntegerField(blank=True, null=True)#quitar
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING, db_column='idcontrato', blank=True, null=True)
    fechainicialvac = models.DateField(blank=True, null=True)
    ultimodiavac = models.DateField(blank=True, null=True)
    diascalendario = models.SmallIntegerField(blank=True, null=True)
    diasvac = models.SmallIntegerField(blank=True, null=True)
    diaspendientes = models.SmallIntegerField(blank=True, null=True)
    idvacaciones = models.IntegerField(primary_key=True)
    pagovac = models.IntegerField(blank=True, null=True)
    totaldiastomados = models.SmallIntegerField(blank=True, null=True)
    basepago = models.IntegerField(blank=True, null=True)
    estadovac = models.SmallIntegerField(blank=True, null=True)
    idnomina = models.IntegerField(blank=True, null=True)
    cuentasabados = models.SmallIntegerField(blank=True, null=True)
    tipovac = models.ForeignKey(Tipoavacaus, models.DO_NOTHING, db_column='tipovac')
    idvacmaster = models.IntegerField(blank=True, null=True)
    perinicio = models.DateField(blank=True, null=True)
    perfinal = models.DateField(blank=True, null=True)
    fechapago = models.DateField(blank=True, null=True)

    class Meta :
        managed = False
        db_table = 'vacaciones'


class VacacionesImportador(models.Model):
    #igual vacaciones 
    id_reg = models.AutoField(primary_key=True)
    cedula = models.BigIntegerField(blank=True, null=True)
    idconcepto = models.SmallIntegerField(blank=True, null=True)
    fechainicialvac = models.DateField(blank=True, null=True)
    ultimodiavac = models.DateField(blank=True, null=True)
    diasvac = models.SmallIntegerField(blank=True, null=True)
    sabados = models.SmallIntegerField(blank=True, null=True)
    perinicio = models.DateField(blank=True, null=True)
    perfinal = models.DateField(blank=True, null=True)
    idnomina = models.BigIntegerField(blank=True, null=True)
    idcontrato = models.BigIntegerField(blank=True, null=True)
    idempleado = models.BigIntegerField(blank=True, null=True)
    pagovac = models.IntegerField(blank=True, null=True)
    basepago = models.IntegerField(blank=True, null=True)
    tipovac = models.SmallIntegerField(blank=True, null=True)
    fechapago = models.DateField(blank=True, null=True)
    tiponovedad = models.SmallIntegerField(blank=True, null=True)
    idvacaciones = models.IntegerField(blank=True, null=True)
    idvacmaster = models.IntegerField(blank=True, null=True)
    estadovac = models.SmallIntegerField(blank=True, null=True)
    diascalendario = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vacaciones_importador'


class VacacionesMaster(models.Model):
    #considerar eliminar 
    idvacmaster = models.IntegerField(primary_key=True)
    idcontrato = models.SmallIntegerField(blank=True, null=True) #fk principal 
    empleado = models.CharField(blank=True, null=True)# 
    titulovac = models.CharField(blank=True, null=True)
    fechapago = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vacaciones_master'


class Zcuentasbancos(models.Model):
    #considerar eliminar 
    idcontrato = models.SmallIntegerField(primary_key=True)
    cuentanomina = models.CharField(max_length=255, blank=True, null=True)
    bancocuenta = models.CharField(max_length=255, blank=True, null=True)
    tipocuentanomina = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'zcuentasbancos'
