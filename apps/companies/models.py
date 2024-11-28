# from django.db import models

# class Contratos(models.Model):
#     cargo = models.CharField(max_length=50, blank=True, null=True)
#     fechainiciocontrato = models.DateField(blank=True, null=True)
#     fechafincontrato = models.DateField(blank=True, null=True)
#     tipocontrato = models.ForeignKey('Tipocontrato', models.DO_NOTHING, db_column='tipocontrato', blank=True, null=True) ## cambiar a entero 
#     tiponomina = models.CharField(max_length=12, blank=True, null=True)
#     bancocuenta = models.CharField(max_length=30, blank=True, null=True)
#     cuentanomina = models.CharField(max_length=30, blank=True, null=True)
#     tipocuentanomina = models.CharField(max_length=15, blank=True, null=True)
#     eps = models.CharField(max_length=125, blank=True, null=True)
#     pension = models.CharField(max_length=125, blank=True, null=True)
#     cajacompensacion = models.CharField(max_length=40, blank=True, null=True)
#     centrotrabajo = models.ForeignKey('Centrotrabajo', models.DO_NOTHING, db_column='centrotrabajo', blank=True, null=True) ## cambiar a entero 
#     tarifaarl = models.CharField(max_length=10, blank=True, null=True)
#     ciudadcontratacion = models.ForeignKey('Ciudades', models.DO_NOTHING, db_column='ciudadcontratacion')
#     fondocesantias = models.CharField(max_length=80, blank=True, null=True)
#     estadocontrato = models.SmallIntegerField(blank=True, null=True)
#     salario = models.IntegerField(blank=True, null=True)
#     idempleado = models.ForeignKey('Contratosemp', models.DO_NOTHING, db_column='idempleado')
#     tipocotizante = models.CharField(max_length=120, blank=True, null=True)
#     subtipocotizante = models.CharField(max_length=120, blank=True, null=True)
#     formapago = models.CharField(max_length=25, blank=True, null=True)
#     metodoretefuente = models.CharField(max_length=25, blank=True, null=True)
#     porcentajeretefuente = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#     valordeduciblevivienda = models.IntegerField(blank=True, null=True)
#     saludretefuente = models.IntegerField(blank=True, null=True)
#     pensionado = models.CharField(max_length=25, blank=True, null=True)
#     estadoliquidacion = models.SmallIntegerField(blank=True, null=True)
#     estadosegsocial = models.SmallIntegerField(blank=True, null=True)
#     motivoretiro = models.CharField(max_length=25, blank=True, null=True)
#     tiposalario = models.ForeignKey('Tiposalario', models.DO_NOTHING, db_column='tiposalario')
#     idcontrato = models.AutoField(primary_key=True)
#     idcosto = models.ForeignKey('Costos', models.DO_NOTHING, db_column='idcosto')
#     idsubcosto = models.ForeignKey('Subcostos', models.DO_NOTHING, db_column='idsubcosto')
#     idsede = models.ForeignKey('Sedes', models.DO_NOTHING, db_column='idsede')
#     salariovariable = models.SmallIntegerField(blank=True, null=True)
#     codeps = models.CharField(max_length=8, blank=True, null=True)
#     codafp = models.CharField(max_length=8, blank=True, null=True)
#     codccf = models.CharField(max_length=8, blank=True, null=True)
#     auxiliotransporte = models.SmallIntegerField(blank=True, null=True)
#     dependientes = models.SmallIntegerField(blank=True, null=True)
#     valordeduciblemedicina = models.IntegerField(blank=True, null=True)
#     jornada = models.CharField(max_length=256,blank=True, null=True)
#     idmodelo = models.ForeignKey('ModelosContratos', models.DO_NOTHING, db_column='idmodelo', blank=True, null=True)
#     coddepartamento = models.CharField(max_length=2, blank=True, null=True)
#     codciudad = models.CharField(max_length=3, blank=True, null=True)
#     riesgo_pension = models.CharField(max_length=5, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'contratos'
    





# class Contratosemp(models.Model):
#     docidentidad = models.BigIntegerField(unique=True)
#     tipodocident = models.CharField(max_length=20, blank=True, null=True)
#     pnombre = models.CharField(max_length=50, blank=True, null=True)
#     snombre = models.CharField(max_length=50, blank=True, null=True)
#     papellido = models.CharField(max_length=50, blank=True, null=True)
#     sapellido = models.CharField(max_length=50, blank=True, null=True)
#     fechanac = models.DateField(blank=True, null=True)
#     ciudadnacimiento = models.TextField(blank=True, null=True)
#     telefonoempleado = models.CharField(max_length=12, blank=True, null=True)
#     direccionempleado = models.CharField(max_length=100, blank=True, null=True)
#     fotografiaempleado = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
#     sexo = models.CharField(max_length=255, blank=True, null=True)
#     email = models.CharField(max_length=255, blank=True, null=True)
#     ciudadresidencia = models.CharField(max_length=20, blank=True, null=True)
#     estadocivil = models.CharField(max_length=20, blank=True, null=True)
#     idempleado = models.AutoField(primary_key=True)
#     paisnacimiento = models.CharField(max_length=40, blank=True, null=True)
#     paisresidencia = models.CharField(max_length=40, blank=True, null=True)
#     celular = models.CharField(max_length=12, blank=True, null=True)
#     profesion = models.CharField(max_length=180, blank=True, null=True)
#     niveleducativo = models.CharField(max_length=25, blank=True, null=True)
#     gruposanguineo = models.CharField(max_length=10, blank=True, null=True)
#     estatura = models.CharField(max_length=10, blank=True, null=True)
#     peso = models.CharField(max_length=10, blank=True, null=True)
#     fechaexpedicion = models.DateField(blank=True, null=True)
#     ciudadexpedicion = models.CharField(max_length=20, blank=True, null=True)
#     dotpantalon = models.CharField(max_length=10, blank=True, null=True)
#     dotcamisa = models.CharField(max_length=10, blank=True, null=True)
#     dotzapatos = models.CharField(max_length=10, blank=True, null=True)
#     estrato = models.CharField(max_length=5, blank=True, null=True)
#     numlibretamil = models.CharField(max_length=10, blank=True, null=True)
#     estadocontrato = models.SmallIntegerField(blank=True, null=True)
#     formatohv = models.CharField(max_length=256,blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'contratosemp'
    
    


# class Costos(models.Model):
#     nomcosto = models.CharField(max_length=30, blank=True, null=True)
#     idcosto = models.AutoField(primary_key=True)
#     grupocontable = models.CharField(max_length=4, blank=True, null=True)
#     suficosto = models.CharField(max_length=2, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'costos'
        
        
#     def __str__(self):
#         return f"{self.nomcosto}"
    

# class ModelosContratos(models.Model):
#     idmodelo = models.SmallIntegerField(primary_key=True)
#     nombremodelo = models.CharField(max_length=255, blank=True, null=True)
#     tipocontrato = models.CharField(max_length=255, blank=True, null=True)
#     textocontrato = models.CharField(max_length=10485760, blank=True, null=True)
#     estadomodelo = models.SmallIntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'modelos_contratos'
        


# class Sedes(models.Model):
#     nombresede = models.CharField(max_length=40, blank=True, null=True)
#     cajacompensacion = models.CharField(max_length=60, blank=True, null=True)
#     idsede = models.AutoField(primary_key=True)
#     codccf = models.CharField(max_length=8, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'sedes'
        


# class Subcostos(models.Model):
#     nomsubcosto = models.CharField(max_length=30, blank=True, null=True)
#     nomcosto = models.CharField(max_length=30, blank=True, null=True)
#     idsubcosto = models.AutoField(primary_key=True)
#     idcosto = models.SmallIntegerField(blank=True, null=True)
#     sufisubcosto = models.CharField(max_length=2, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'subcostos'
        
#     def __str__(self):
#         return f"{self.nomsubcosto}"

# class Tipocontrato(models.Model):
#     idtipocontrato = models.IntegerField(primary_key=True)
#     tipocontrato = models.CharField(max_length=255, blank=True, null=True)
#     cod_dian = models.SmallIntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tipocontrato'
        
#     def __str__(self):
#         return f"{self.tipocontrato}"

# class Centrotrabajo(models.Model):
#     nombrecentrotrabajo = models.CharField(max_length=30, blank=True, null=True)
#     tarifaarl = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
#     centrotrabajo = models.AutoField(primary_key=True)

#     class Meta:
#         managed = False
#         db_table = 'centrotrabajo'
        
#     def __str__(self):
#         return f"{self.nombrecentrotrabajo}"

        
        
# class Tipodocumento(models.Model):
#     id_tipo_doc = models.CharField(max_length=10, primary_key=True)
#     documento = models.CharField(max_length=50, blank=True, null=True)
#     codigo = models.CharField(max_length=4, blank=True, null=True)
#     cod_dian = models.SmallIntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tipodocumento'
        

# class Profesiones(models.Model):
#     idprofesion = models.SmallIntegerField(primary_key=True)
#     profesion = models.CharField(max_length=180, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'profesiones'



# class Paises(models.Model):
#     idpais = models.CharField(max_length=10, primary_key=True)
#     pais = models.CharField(max_length=50, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'paises'
    

# class Ciudades(models.Model):
#     idciudad = models.CharField(max_length=10, primary_key=True)
#     ciudad = models.CharField(max_length=50, db_collation='es_ES', blank=True, null=True)
#     departamento = models.CharField(max_length=50, db_collation='es_ES', blank=True, null=True)
#     codciudad = models.CharField(max_length=10, blank=True, null=True)
#     coddepartamento = models.CharField(max_length=10, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'ciudades'
        
        
        
        

# class Tiposalario(models.Model):
#     idtiposalario = models.SmallIntegerField(primary_key=True)
#     tiposalario = models.CharField(max_length=40, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tiposalario'

#     def __str__(self):
#         return f"{self.tiposalario}"
        

# class Cargos(models.Model):
#     idcargo = models.AutoField(primary_key=True)
#     nombrecargo = models.CharField(max_length=50)
#     nombrenivel = models.CharField(max_length=50, blank=True, null=True)
#     cargojefe = models.CharField(max_length=50, blank=True, null=True)
#     cargosacargo = models.CharField(blank=True, null=True)
#     estado = models.BooleanField()

#     class Meta:
#         managed = False
#         db_table = 'cargos'

#     def save(self, *args, **kwargs):
#         self.estado = True
#         super().save(*args, **kwargs)

        
# class Bancos(models.Model):
#     idbanco = models.IntegerField(primary_key=True)
#     nombanco = models.CharField(max_length=255, blank=True, null=True)
#     codbanco = models.CharField(max_length=255, blank=True, null=True)
#     codach = models.CharField(max_length=255, blank=True, null=True)
#     digchequeo = models.CharField(max_length=255, blank=True, null=True)
#     nitbanco = models.CharField(max_length=255, blank=True, null=True)
#     tamcorriente = models.CharField(max_length=255, blank=True, null=True)
#     tamahorro = models.CharField(max_length=255, blank=True, null=True)
#     oficina = models.CharField(max_length=255, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'bancos'
        
#     def __str__(self):
#         return f"{self.nombanco}"
    
# class Entidadessegsocial(models.Model):
#     codigo = models.CharField(primary_key=True, max_length=9)
#     nit = models.CharField(max_length=12)
#     entidad = models.CharField(max_length=120)
#     tipoentidad = models.CharField(max_length=20)
#     codsgp = models.CharField(max_length=10, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'entidadessegsocial'
        
        
        
        
# class Tipodenomina(models.Model):
#     idtiponomina = models.IntegerField(primary_key=True)
#     tipodenomina = models.CharField(max_length=255)
#     cod_dian = models.SmallIntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tipodenomina'
    
    

# class Contabgrupos(models.Model):
#     idgrupo = models.CharField(primary_key=True, max_length=2)
#     grupocontable = models.CharField(max_length=40, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'contabgrupos'
        



# ##* nomina : 

# class Nomina(models.Model):
#     idregistronom = models.IntegerField(primary_key=True)
#     nombreconcepto = models.CharField(max_length=255, blank=True, null=True)
#     valor = models.IntegerField(blank=True, null=True)
#     mesacumular = models.CharField(max_length=15, blank=True, null=True)
#     anoacumular = models.CharField(max_length=15, blank=True, null=True)
#     idempleado = models.ForeignKey(Contratosemp, models.DO_NOTHING, db_column='idempleado', blank=True, null=True)
#     cantidad = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
#     idconcepto = models.ForeignKey('Conceptosdenomina', models.DO_NOTHING, db_column='idconcepto')
#     idnomina = models.ForeignKey('Crearnomina', models.DO_NOTHING, db_column='idnomina')
#     estadonomina = models.SmallIntegerField(blank=True, null=True)
#     idcontrato = models.ForeignKey('Contratos', models.DO_NOTHING, db_column='idcontrato')
#     idcosto = models.ForeignKey('Costos', models.DO_NOTHING, db_column='idcosto')
#     idsubcosto = models.ForeignKey('Subcostos', models.DO_NOTHING, db_column='idsubcosto')
#     control = models.IntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'nomina'

# class Conceptosdenomina(models.Model):
#     nombreconcepto = models.CharField(max_length=30)
#     multiplicadorconcepto = models.DecimalField(max_digits=4, decimal_places=2)
#     tipoconcepto = models.IntegerField()
#     sueldobasico = models.IntegerField(blank=True, null=True)
#     auxtransporte = models.IntegerField(blank=True, null=True)
#     baseprestacionsocial = models.IntegerField(blank=True, null=True)
#     ingresotributario = models.IntegerField(blank=True, null=True)
#     prestacionsocial = models.IntegerField(blank=True, null=True)
#     extras = models.IntegerField(blank=True, null=True)
#     basesegsocial = models.IntegerField(blank=True, null=True)
#     cuentacontable = models.CharField(max_length=25, blank=True, null=True)
#     idconcepto = models.IntegerField(primary_key=True)
#     ausencia = models.IntegerField(blank=True, null=True)
#     salintegral = models.IntegerField(blank=True, null=True)
#     basevacaciones = models.IntegerField(blank=True, null=True)
#     formula = models.CharField(max_length=1, blank=True, null=True)
#     basetransporte = models.SmallIntegerField(blank=True, null=True)
#     aportess = models.SmallIntegerField(blank=True, null=True)
#     incapacidad = models.SmallIntegerField(blank=True, null=True)
#     base1393 = models.SmallIntegerField(blank=True, null=True)
#     norenta = models.SmallIntegerField(blank=True, null=True)
#     pension = models.SmallIntegerField(blank=True, null=True)
#     exentos = models.SmallIntegerField(blank=True, null=True)
#     baserarl = models.SmallIntegerField(blank=True, null=True)
#     basecaja = models.SmallIntegerField(blank=True, null=True)
#     viaticos = models.SmallIntegerField(blank=True, null=True)
#     comisiones = models.SmallIntegerField(blank=True, null=True)
#     gastosderep = models.SmallIntegerField(blank=True, null=True)
#     suspcontrato = models.SmallIntegerField(blank=True, null=True)
#     grupo_dian = models.CharField(max_length=255, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'conceptosdenomina'

# class Crearnomina(models.Model):
#     nombrenomina = models.CharField(max_length=40, blank=True, null=True)
#     fechainicial = models.DateField(blank=True, null=True)
#     fechafinal = models.DateField(blank=True, null=True)
#     fechapago = models.DateField(blank=True, null=True)
#     tipodenomina = models.CharField(max_length=2, blank=True, null=True)
#     mesacumular = models.CharField(max_length=20, blank=True, null=True)
#     anoacumular = models.CharField(max_length=4, blank=True, null=True)
#     estadonomina = models.SmallIntegerField(blank=True, null=True)
#     diasnomina = models.SmallIntegerField(blank=True, null=True)
#     idnomina = models.IntegerField(primary_key=True)
    

#     class Meta:
#         managed = False
#         db_table = 'crearnomina'
        
# class NominaComprobantes(models.Model):
#     idhistorico = models.AutoField(primary_key=True)
#     idcontrato = models.IntegerField(blank=True, null=True)
#     salario = models.IntegerField(blank=True, null=True)
#     cargo = models.CharField(max_length=120, blank=True, null=True)
#     idcosto = models.SmallIntegerField(blank=True, null=True)
#     pension = models.CharField(max_length=125, blank=True, null=True)
#     salud = models.CharField(max_length=125, blank=True, null=True)
#     idnomina = models.IntegerField(blank=True, null=True)
#     envio_email = models.SmallIntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'nomina_comprobantes'
        
        
        
        
# ## liquidaciones 


# class Liquidacion(models.Model):
#     idliquidacion = models.IntegerField(primary_key=True)  # The composite primary key (idliquidacion, idcontrato) found, that is not supported. The first column is selected.
#     docidentidad = models.CharField(max_length=15, blank=True, null=True)
#     diastrabajados = models.CharField(max_length=8, blank=True, null=True)
#     cesantias = models.CharField(max_length=30, blank=True, null=True)
#     prima = models.CharField(max_length=30, blank=True, null=True)
#     vacaciones = models.CharField(max_length=30, blank=True, null=True)
#     intereses = models.CharField(max_length=30, blank=True, null=True)
#     totalliq = models.CharField(max_length=30, blank=True, null=True)
#     diascesantias = models.CharField(max_length=8, blank=True, null=True)
#     diasprimas = models.CharField(max_length=8, blank=True, null=True)
#     diasvacaciones = models.CharField(max_length=8, blank=True, null=True)
#     baseprima = models.CharField(max_length=30, blank=True, null=True)
#     basecesantias = models.CharField(max_length=30, blank=True, null=True)
#     basevacaciones = models.CharField(max_length=30, blank=True, null=True)
#     idcontrato = models.ForeignKey('Contratos', models.DO_NOTHING, db_column='idcontrato')
#     idempleado = models.ForeignKey('Contratosemp', models.DO_NOTHING, db_column='idempleado')
#     fechainiciocontrato = models.DateField(blank=True, null=True)
#     fechafincontrato = models.DateField(blank=True, null=True)
#     salario = models.IntegerField(blank=True, null=True)
#     motivoretiro = models.CharField(blank=True, null=True)
#     estadoliquidacion = models.CharField(blank=True, null=True)
#     diassusp = models.SmallIntegerField(blank=True, null=True)
#     indemnizacion = models.IntegerField(blank=True, null=True)
#     diassuspv = models.SmallIntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'liquidacion'
#         unique_together = (('idliquidacion', 'idcontrato'),)


# class LiquidacionMasivo(models.Model):
#     idliquidacion = models.IntegerField(primary_key=True)  # The composite primary key (idliquidacion, idcontrato) found, that is not supported. The first column is selected.
#     docidentidad = models.CharField(max_length=15, blank=True, null=True)
#     diastrabajados = models.CharField(max_length=8, blank=True, null=True)
#     cesantias = models.CharField(max_length=30, blank=True, null=True)
#     prima = models.CharField(max_length=30, blank=True, null=True)
#     vacaciones = models.CharField(max_length=30, blank=True, null=True)
#     intereses = models.CharField(max_length=30, blank=True, null=True)
#     totalliq = models.CharField(max_length=30, blank=True, null=True)
#     diascesantias = models.CharField(max_length=8, blank=True, null=True)
#     diasprimas = models.CharField(max_length=8, blank=True, null=True)
#     diasvacaciones = models.CharField(max_length=8, blank=True, null=True)
#     baseprima = models.CharField(max_length=30, blank=True, null=True)
#     basecesantias = models.CharField(max_length=30, blank=True, null=True)
#     basevacaciones = models.CharField(max_length=30, blank=True, null=True)
#     idcontrato = models.IntegerField()
#     idempleado = models.IntegerField(blank=True, null=True)
#     fechainiciocontrato = models.DateField(blank=True, null=True)
#     fechafincontrato = models.DateField(blank=True, null=True)
#     salario = models.IntegerField(blank=True, null=True)
#     motivoretiro = models.CharField(blank=True, null=True)
#     estadoliquidacion = models.CharField(blank=True, null=True)
#     diassusp = models.SmallIntegerField(blank=True, null=True)
#     indemnizacion = models.IntegerField(blank=True, null=True)
#     diassuspv = models.CharField(max_length=16, blank=True, null=True)
#     idcosto = models.SmallIntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'liquidacion_masivo'
#         unique_together = (('idliquidacion', 'idcontrato'),)



# class Conceptosfijos(models.Model):
#     idfijo = models.IntegerField(primary_key=True)
#     conceptofijo = models.CharField(max_length=80, blank=True, null=True)
#     valorfijo = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'conceptosfijos'


# class Salariominimoanual(models.Model):
#     idano = models.SmallIntegerField(primary_key=True)
#     salariominimo = models.IntegerField(blank=True, null=True)
#     auxtransporte = models.IntegerField(blank=True, null=True)
#     uvt = models.IntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'salariominimoanual'
        
        
# # prestamos 


# class Prestamos(models.Model):
#     idprestamo = models.AutoField(primary_key=True)
#     idcontrato = models.ForeignKey('Contratos', models.DO_NOTHING, db_column='idcontrato')
#     idempleado = models.ForeignKey('Contratosemp', models.DO_NOTHING, db_column='idempleado')
#     valorprestamo = models.IntegerField(blank=True, null=True)
#     fechaprestamo = models.DateField(blank=True, null=True)
#     cuotasprestamo = models.SmallIntegerField(blank=True, null=True)
#     valorcuota = models.IntegerField(blank=True, null=True)
#     saldoprestamo = models.IntegerField(blank=True, null=True)
#     cuotaspagadas = models.SmallIntegerField(blank=True, null=True)
#     empleado = models.CharField(max_length=40, blank=True, null=True)
#     estadoprestamo = models.BooleanField(blank=True, null=True)
#     formapago = models.SmallIntegerField(blank=True, null=True)
#     diapago = models.SmallIntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'prestamos'




# class Incapacidades(models.Model):
#     idincapacidad = models.AutoField(primary_key=True)
#     empleado = models.CharField(max_length=80, blank=True, null=True)
#     certificadoincapacidad = models.CharField(max_length=15, blank=True, null=True)
#     tipoentidad = models.CharField(max_length=5, blank=True, null=True)
#     entidad = models.CharField(max_length=80, blank=True, null=True)
#     coddiagnostico = models.ForeignKey('Diagnosticosenfermedades', models.DO_NOTHING, db_column='coddiagnostico')
#     diagnostico = models.CharField(max_length=255, blank=True, null=True)
#     fechainicial = models.DateField(blank=True, null=True)
#     dias = models.IntegerField(blank=True, null=True)
#     nominaincap = models.CharField(max_length=30, blank=True, null=True)
#     imagenincapacidad = models.CharField(blank=True, null=True)
#     idempleado = models.ForeignKey('Contratosemp', models.DO_NOTHING, db_column='idempleado')
#     idcontrato = models.ForeignKey('Contratos', models.DO_NOTHING, db_column='idcontrato')
#     estadonovincap = models.SmallIntegerField(blank=True, null=True)
#     prorroga = models.CharField(max_length=5, blank=True, null=True)
#     ibc = models.IntegerField(blank=True, null=True)
#     saldodias = models.SmallIntegerField(blank=True, null=True)
#     origenincap = models.CharField(blank=True, null=True)
#     finincap = models.DateField(blank=True, null=True)
#     imagenblob = models.BinaryField(blank=True, null=True)
#     liq = models.CharField(max_length=255, blank=True, null=True)
#     prefijo = models.CharField(max_length=7, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'incapacidades'
        
# class Diagnosticosenfermedades(models.Model):
#     coddiagnostico = models.CharField(primary_key=True, max_length=255)
#     diagnostico = models.CharField(max_length=255, blank=True, null=True)
#     prefijo = models.CharField(max_length=1, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'diagnosticosenfermedades'
        
        
# class Tipoavacaus(models.Model):
#     tipovac = models.CharField(primary_key=True, max_length=255)
#     nombrevacaus = models.CharField(max_length=30, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tipoavacaus'


# class Vacaciones(models.Model):
#     idempleado = models.SmallIntegerField(blank=True, null=True)
#     idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING, db_column='idcontrato', blank=True, null=True)
#     fechainicialvac = models.DateField(blank=True, null=True)
#     ultimodiavac = models.DateField(blank=True, null=True)
#     diascalendario = models.SmallIntegerField(blank=True, null=True)
#     diasvac = models.SmallIntegerField(blank=True, null=True)
#     diaspendientes = models.SmallIntegerField(blank=True, null=True)
#     idvacaciones = models.IntegerField(primary_key=True)
#     pagovac = models.IntegerField(blank=True, null=True)
#     totaldiastomados = models.SmallIntegerField(blank=True, null=True)
#     basepago = models.IntegerField(blank=True, null=True)
#     estadovac = models.SmallIntegerField(blank=True, null=True)
#     idnomina = models.IntegerField(blank=True, null=True)
#     cuentasabados = models.SmallIntegerField(blank=True, null=True)
#     tipovac = models.ForeignKey(Tipoavacaus, models.DO_NOTHING, db_column='tipovac')
#     idvacmaster = models.IntegerField(blank=True, null=True)
#     perinicio = models.DateField(blank=True, null=True)
#     perfinal = models.DateField(blank=True, null=True)
#     fechapago = models.DateField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'vacaciones'
        
