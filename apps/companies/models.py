from django.db import models

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
    

class ModelosContratos(models.Model):
    idmodelo = models.SmallIntegerField(primary_key=True)
    nombremodelo = models.CharField(max_length=255, blank=True, null=True)
    tipocontrato = models.CharField(max_length=255, blank=True, null=True)
    textocontrato = models.CharField(max_length=10485760, blank=True, null=True)
    estadomodelo = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'modelos_contratos'
        


class Sedes(models.Model):
    nombresede = models.CharField(max_length=40, blank=True, null=True)
    cajacompensacion = models.CharField(max_length=60, blank=True, null=True)
    idsede = models.SmallIntegerField(primary_key=True)
    codccf = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sedes'
        
    def __str__(self):
        return f"{self.nombremodelo}"


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

class Tipocontrato(models.Model):
    idtipocontrato = models.IntegerField(primary_key=True)
    tipocontrato = models.CharField(max_length=255, blank=True, null=True)
    cod_dian = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipocontrato'
        
    def __str__(self):
        return f"{self.tipocontrato}"

class Centrotrabajo(models.Model):
    nombrecentrotrabajo = models.CharField(max_length=30, blank=True, null=True)
    tarifaarl = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    centrotrabajo = models.SmallIntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'centrotrabajo'
        
    def __str__(self):
        return f"{self.nombrecentrotrabajo}"

        
        
class Tipodocumento(models.Model):
    id_tipo_doc = models.CharField(max_length=10, primary_key=True)
    documento = models.CharField(max_length=50, blank=True, null=True)
    codigo = models.CharField(max_length=4, blank=True, null=True)
    cod_dian = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipodocumento'
        

class Profesiones(models.Model):
    idprofesion = models.SmallIntegerField(primary_key=True)
    profesion = models.CharField(max_length=180, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'profesiones'



class Paises(models.Model):
    idpais = models.CharField(max_length=10, primary_key=True)
    pais = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'paises'
    

class Ciudades(models.Model):
    idciudad = models.CharField(max_length=10, primary_key=True)
    ciudad = models.CharField(max_length=50, db_collation='es_ES', blank=True, null=True)
    departamento = models.CharField(max_length=50, db_collation='es_ES', blank=True, null=True)
    codciudad = models.CharField(max_length=10, blank=True, null=True)
    coddepartamento = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ciudades'
        
        
        
class Tiposalario(models.Model):
    idtiposalario = models.SmallIntegerField(primary_key=True)
    tiposalario = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tiposalario'
        
class Tiposalario(models.Model):
    idtiposalario = models.SmallIntegerField(primary_key=True)
    tiposalario = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tiposalario'

    def __str__(self):
        return f"{self.tiposalario}"
        
