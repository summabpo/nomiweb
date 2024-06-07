from django.db import models

# Create your models here.


class Contratos(models.Model):
    cargo = models.CharField(max_length=50, blank=True, null=True)
    fechainiciocontrato = models.DateField(blank=True, null=True)
    fechafincontrato = models.DateField(blank=True, null=True)
    tipocontrato = models.ForeignKey('Tipocontrato', models.DO_NOTHING, db_column='tipocontrato', blank=True, null=True) ## cambiar a entero 
    tiponomina = models.CharField(max_length=12, blank=True, null=True)
    bancocuenta = models.CharField(max_length=30, blank=True, null=True)
    cuentanomina = models.CharField(max_length=30, blank=True, null=True)
    tipocuentanomina = models.CharField(max_length=15, blank=True, null=True)
    eps = models.CharField(max_length=125, blank=True, null=True)
    pension = models.CharField(max_length=125, blank=True, null=True)
    cajacompensacion = models.CharField(max_length=40, blank=True, null=True)
    centrotrabajo = models.ForeignKey('Centrotrabajo', models.DO_NOTHING, db_column='centrotrabajo', blank=True, null=True) ## cambiar a entero 
    tarifaarl = models.CharField(max_length=10, blank=True, null=True)
    ciudadcontratacion = models.ForeignKey('Ciudades', models.DO_NOTHING, db_column='ciudadcontratacion')
    fondocesantias = models.CharField(max_length=80, blank=True, null=True)
    estadocontrato = models.SmallIntegerField(blank=True, null=True)
    salario = models.IntegerField(blank=True, null=True)
    idempleado = models.ForeignKey('Contratosemp', models.DO_NOTHING, db_column='idempleado')
    tipocotizante = models.CharField(max_length=120, blank=True, null=True)
    subtipocotizante = models.CharField(max_length=120, blank=True, null=True)
    formapago = models.CharField(max_length=25, blank=True, null=True)
    metodoretefuente = models.CharField(max_length=25, blank=True, null=True)
    porcentajeretefuente = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    valordeduciblevivienda = models.IntegerField(blank=True, null=True)
    saludretefuente = models.IntegerField(blank=True, null=True)
    pensionado = models.CharField(max_length=25, blank=True, null=True)
    estadoliquidacion = models.SmallIntegerField(blank=True, null=True)
    estadosegsocial = models.SmallIntegerField(blank=True, null=True)
    motivoretiro = models.CharField(max_length=25, blank=True, null=True)
    tiposalario = models.ForeignKey('Tiposalario', models.DO_NOTHING, db_column='tiposalario')
    idcontrato = models.AutoField(primary_key=True)
    idcosto = models.ForeignKey('Costos', models.DO_NOTHING, db_column='idcosto')
    idsubcosto = models.ForeignKey('Subcostos', models.DO_NOTHING, db_column='idsubcosto')
    idsede = models.ForeignKey('Sedes', models.DO_NOTHING, db_column='idsede')
    salariovariable = models.SmallIntegerField(blank=True, null=True)
    codeps = models.CharField(max_length=8, blank=True, null=True)
    codafp = models.CharField(max_length=8, blank=True, null=True)
    codccf = models.CharField(max_length=8, blank=True, null=True)
    auxiliotransporte = models.SmallIntegerField(blank=True, null=True)
    dependientes = models.SmallIntegerField(blank=True, null=True)
    valordeduciblemedicina = models.IntegerField(blank=True, null=True)
    jornada = models.CharField(max_length=256,blank=True, null=True)
    idmodelo = models.ForeignKey('ModelosContratos', models.DO_NOTHING, db_column='idmodelo', blank=True, null=True)
    coddepartamento = models.CharField(max_length=2, blank=True, null=True)
    codciudad = models.CharField(max_length=3, blank=True, null=True)
    riesgo_pension = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contratos'
    
class Certificaciones(models.Model):
    idcert = models.AutoField(primary_key=True)
    destino = models.CharField(max_length=100, blank=True, null=True)
    idempleado = models.ForeignKey('Contratosemp', models.DO_NOTHING, db_column='idempleado')
    idcontrato = models.IntegerField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    salario = models.IntegerField(blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    tipocontrato = models.CharField(max_length=30, blank=True, null=True)
    promediovariable = models.IntegerField(blank=True, null=True)
    codigoconfirmacion = models.CharField(max_length=8, blank=True, null=True)
    tipocertificacion = models.IntegerField(blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'certificaciones'

class Tipocontrato(models.Model):
    idtipocontrato = models.IntegerField(primary_key=True)
    tipocontrato = models.CharField(max_length=255, blank=True, null=True)
    cod_dian = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipocontrato'

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
    website = models.CharField(max_length=40, blank=True, null=True)
    metodoextras = models.CharField(max_length=1, blank=True, null=True)
    dv = models.CharField(max_length=1, blank=True, null=True)
    coddpto = models.CharField(max_length=3, blank=True, null=True)
    codciudad = models.CharField(max_length=3, blank=True, null=True)
    nomciudad = models.CharField(max_length=40, blank=True, null=True)
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
class Crearnomina(models.Model):
    nombrenomina = models.CharField(max_length=40, blank=True, null=True)
    fechainicial = models.DateField(blank=True, null=True)
    fechafinal = models.DateField(blank=True, null=True)
    fechapago = models.DateField(blank=True, null=True)
    tipodenomina = models.CharField(max_length=2, blank=True, null=True)
    mesacumular = models.CharField(max_length=20, blank=True, null=True)
    anoacumular = models.CharField(max_length=4, blank=True, null=True)
    estadonomina = models.SmallIntegerField(blank=True, null=True)
    diasnomina = models.SmallIntegerField(blank=True, null=True)
    idnomina = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'crearnomina'
class Conceptosdenomina(models.Model):
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

class Nomina(models.Model):
    idregistronom = models.IntegerField(primary_key=True)
    nombreconcepto = models.CharField(max_length=255, blank=True, null=True)
    valor = models.IntegerField(blank=True, null=True)
    mesacumular = models.CharField(max_length=15, blank=True, null=True)
    anoacumular = models.CharField(max_length=15, blank=True, null=True)
    idempleado = models.IntegerField(blank=True, null=True)
    cantidad = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    idconcepto = models.ForeignKey(Conceptosdenomina, models.DO_NOTHING, db_column='idconcepto', blank=True, null=True)
    idnomina = models.ForeignKey(Crearnomina, models.DO_NOTHING, db_column='idnomina', blank=True, null=True)
    estadonomina = models.SmallIntegerField(blank=True, null=True)
    idcontrato = models.IntegerField(blank=True, null=True)
    idcosto = models.SmallIntegerField(blank=True, null=True)
    idsubcosto = models.SmallIntegerField(blank=True, null=True)
    control = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nomina'

class Contratosemp(models.Model):
    docidentidad = models.BigIntegerField(unique=True)
    tipodocident = models.CharField(max_length=20, blank=True, null=True)
    pnombre = models.CharField(max_length=50, blank=True, null=True)
    snombre = models.CharField(max_length=50, blank=True, null=True)
    papellido = models.CharField(max_length=50, blank=True, null=True)
    sapellido = models.CharField(max_length=50, blank=True, null=True)
    fechanac = models.DateField(blank=True, null=True)
    ciudadnacimiento = models.TextField(blank=True, null=True)
    telefonoempleado = models.CharField(max_length=12, blank=True, null=True)
    direccionempleado = models.CharField(max_length=100, blank=True, null=True)
    fotografiaempleado = models.BinaryField(blank=True, null=True)
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
    formatohv = models.CharField(max_length=256,blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contratosemp'
    




class Centrotrabajo(models.Model):
    nombrecentrotrabajo = models.CharField(max_length=30, blank=True, null=True)
    tarifaarl = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    centrotrabajo = models.SmallIntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'centrotrabajo'
        
    def __str__(self):
        return f"{self.nombrecentrotrabajo}"

        
      

class Tiposalario(models.Model):
    idtiposalario = models.SmallIntegerField(primary_key=True)
    tiposalario = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tiposalario'

    def __str__(self):
        return f"{self.tiposalario}"
    
class Costos(models.Model):
    nomcosto = models.CharField(max_length=30, blank=True, null=True)
    idcosto = models.SmallIntegerField(primary_key=True)
    grupocontable = models.CharField(max_length=4, blank=True, null=True)
    suficosto = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'costos'
        
        
    def __str__(self):
        return f"{self.nomcosto}"
    
class Subcostos(models.Model):
    nomsubcosto = models.CharField(max_length=30, blank=True, null=True)
    nomcosto = models.CharField(max_length=30, blank=True, null=True)
    idsubcosto = models.SmallIntegerField(primary_key=True)
    idcosto = models.SmallIntegerField(blank=True, null=True)
    sufisubcosto = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subcostos'
        
    def __str__(self):
        return f"{self.nomsubcosto}"


class Sedes(models.Model):
    nombresede = models.CharField(max_length=40, blank=True, null=True)
    cajacompensacion = models.CharField(max_length=60, blank=True, null=True)
    idsede = models.SmallIntegerField(primary_key=True)
    codccf = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sedes'
        

class ModelosContratos(models.Model):
    idmodelo = models.SmallIntegerField(primary_key=True)
    nombremodelo = models.CharField(max_length=255, blank=True, null=True)
    tipocontrato = models.CharField(max_length=255, blank=True, null=True)
    textocontrato = models.CharField(max_length=10485760, blank=True, null=True)
    estadomodelo = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'modelos_contratos'
        

class Ciudades(models.Model):
    idciudad = models.CharField(max_length=10, primary_key=True)
    ciudad = models.CharField(max_length=50, db_collation='es_ES', blank=True, null=True)
    departamento = models.CharField(max_length=50, db_collation='es_ES', blank=True, null=True)
    codciudad = models.CharField(max_length=10, blank=True, null=True)
    coddepartamento = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ciudades'

class Tipoavacaus(models.Model):
    tipovac = models.CharField(max_length=10, primary_key=True)
    nombrevacaus = models.CharField(max_length=30, blank=True, null=True)
    
    def __str__(self):
        return self.nombrevacaus

    class Meta:
        managed = False
        db_table = 'tipoavacaus'
class Vacaciones(models.Model):
    idempleado = models.ForeignKey(Contratosemp, models.DO_NOTHING, db_column='idempleado', blank=True, null=True)
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
    tipovac = models.ForeignKey(Tipoavacaus, models.DO_NOTHING, db_column='tipovac', blank=True, null=True)
    idvacmaster = models.IntegerField(blank=True, null=True)
    perinicio = models.DateField(blank=True, null=True)
    perfinal = models.DateField(blank=True, null=True)
    fechapago = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vacaciones'

class EmpVacaciones(models.Model):
    id_sol_vac = models.AutoField(primary_key=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING, db_column='idcontrato', blank=True, null=True)
    tipovac = models.ForeignKey(Tipoavacaus, models.DO_NOTHING, db_column='tipovac', blank=True, null=True)
    fechainicialvac = models.DateField(blank=True, null=True)
    fechafinalvac = models.DateField(blank=True, null=True)
    estado = models.SmallIntegerField(blank=True, null=True)
    diasvac = models.SmallIntegerField(blank=True, null=True)
    cuentasabados = models.SmallIntegerField(blank=True, null=True)
    diascalendario = models.SmallIntegerField(blank=True, null=True)
    idempleado = models.ForeignKey(Contratosemp, models.DO_NOTHING, db_column='idempleado', blank=True, null=True)
    ip_usuario = models.CharField(max_length=16, blank=True, null=True)
    fecha_hora = models.DateTimeField(blank=True, null=True)
    update = models.DateTimeField(blank=True, null=True)
    comentarios = models.CharField(max_length=255, blank=True, null=True)
    comentarios2 = models.CharField(max_length=255, blank=True, null=True)
    update_ip = models.CharField(max_length=16, blank=True, null=True)
    
    def __str__(self):
        return f"{self.idcontrato} - {self.tipovac}"

    class Meta:
        managed = False
        db_table = 'emp_vacaciones'
class Festivos(models.Model):
    idfestivo = models.IntegerField(primary_key=True)
    dia = models.DateField(blank=True, null=True)
    descripcion = models.CharField(max_length=60, blank=True, null=True)
    ano = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'festivos'
