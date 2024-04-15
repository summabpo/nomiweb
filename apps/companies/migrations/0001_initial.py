# Generated by Django 5.0.3 on 2024-04-12 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Centrotrabajo',
            fields=[
                ('nombrecentrotrabajo', models.CharField(blank=True, max_length=30, null=True)),
                ('tarifaarl', models.DecimalField(blank=True, decimal_places=3, max_digits=5, null=True)),
                ('centrotrabajo', models.SmallIntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'centrotrabajo',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Contratos',
            fields=[
                ('cargo', models.CharField(blank=True, max_length=50, null=True)),
                ('fechainiciocontrato', models.DateField(blank=True, null=True)),
                ('fechafincontrato', models.DateField(blank=True, null=True)),
                ('tipocontrato', models.CharField(blank=True, max_length=40, null=True)),
                ('tiponomina', models.CharField(blank=True, max_length=12, null=True)),
                ('bancocuenta', models.CharField(blank=True, max_length=30, null=True)),
                ('cuentanomina', models.CharField(blank=True, max_length=30, null=True)),
                ('tipocuentanomina', models.CharField(blank=True, max_length=15, null=True)),
                ('eps', models.CharField(blank=True, max_length=125, null=True)),
                ('pension', models.CharField(blank=True, max_length=125, null=True)),
                ('cajacompensacion', models.CharField(blank=True, max_length=40, null=True)),
                ('centrotrabajo', models.CharField(blank=True, max_length=30, null=True)),
                ('tarifaarl', models.CharField(blank=True, max_length=10, null=True)),
                ('ciudadcontratacion', models.CharField(blank=True, max_length=40, null=True)),
                ('fondocesantias', models.CharField(blank=True, max_length=80, null=True)),
                ('estadocontrato', models.SmallIntegerField(blank=True, null=True)),
                ('salario', models.IntegerField(blank=True, null=True)),
                ('tipocotizante', models.CharField(blank=True, max_length=120, null=True)),
                ('subtipocotizante', models.CharField(blank=True, max_length=120, null=True)),
                ('formapago', models.CharField(blank=True, max_length=25, null=True)),
                ('metodoretefuente', models.CharField(blank=True, max_length=25, null=True)),
                ('porcentajeretefuente', models.DecimalField(blank=True, decimal_places=65535, max_digits=65535, null=True)),
                ('valordeduciblevivienda', models.IntegerField(blank=True, null=True)),
                ('saludretefuente', models.IntegerField(blank=True, null=True)),
                ('pensionado', models.CharField(blank=True, max_length=25, null=True)),
                ('estadoliquidacion', models.SmallIntegerField(blank=True, null=True)),
                ('estadosegsocial', models.SmallIntegerField(blank=True, null=True)),
                ('motivoretiro', models.CharField(blank=True, max_length=25, null=True)),
                ('tiposalario', models.SmallIntegerField(blank=True, null=True)),
                ('idcontrato', models.IntegerField(primary_key=True, serialize=False)),
                ('salariovariable', models.SmallIntegerField(blank=True, null=True)),
                ('codeps', models.CharField(blank=True, max_length=8, null=True)),
                ('codafp', models.CharField(blank=True, max_length=8, null=True)),
                ('codccf', models.CharField(blank=True, max_length=8, null=True)),
                ('auxiliotransporte', models.SmallIntegerField(blank=True, null=True)),
                ('dependientes', models.SmallIntegerField(blank=True, null=True)),
                ('valordeduciblemedicina', models.IntegerField(blank=True, null=True)),
                ('jornada', models.CharField(blank=True, null=True)),
                ('coddepartamento', models.CharField(blank=True, max_length=2, null=True)),
                ('codciudad', models.CharField(blank=True, max_length=3, null=True)),
                ('riesgo_pension', models.CharField(blank=True, max_length=5, null=True)),
            ],
            options={
                'db_table': 'contratos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Contratosemp',
            fields=[
                ('docidentidad', models.BigIntegerField(unique=True)),
                ('tipodocident', models.CharField(blank=True, max_length=20, null=True)),
                ('pnombre', models.CharField(blank=True, max_length=50, null=True)),
                ('snombre', models.CharField(blank=True, max_length=50, null=True)),
                ('papellido', models.CharField(blank=True, max_length=50, null=True)),
                ('sapellido', models.CharField(blank=True, max_length=50, null=True)),
                ('fechanac', models.DateField(blank=True, null=True)),
                ('ciudadnacimiento', models.TextField(blank=True, null=True)),
                ('telefonoempleado', models.CharField(blank=True, max_length=12, null=True)),
                ('direccionempleado', models.CharField(blank=True, max_length=100, null=True)),
                ('fotografiaempleado', models.BinaryField(blank=True, null=True)),
                ('sexo', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('ciudadresidencia', models.CharField(blank=True, max_length=20, null=True)),
                ('estadocivil', models.CharField(blank=True, max_length=20, null=True)),
                ('idempleado', models.IntegerField(primary_key=True, serialize=False)),
                ('paisnacimiento', models.CharField(blank=True, max_length=40, null=True)),
                ('paisresidencia', models.CharField(blank=True, max_length=40, null=True)),
                ('celular', models.CharField(blank=True, max_length=12, null=True)),
                ('profesion', models.CharField(blank=True, max_length=180, null=True)),
                ('niveleducativo', models.CharField(blank=True, max_length=25, null=True)),
                ('gruposanguineo', models.CharField(blank=True, max_length=10, null=True)),
                ('estatura', models.CharField(blank=True, max_length=10, null=True)),
                ('peso', models.CharField(blank=True, max_length=10, null=True)),
                ('fechaexpedicion', models.DateField(blank=True, null=True)),
                ('ciudadexpedicion', models.CharField(blank=True, max_length=20, null=True)),
                ('dotpantalon', models.CharField(blank=True, max_length=10, null=True)),
                ('dotcamisa', models.CharField(blank=True, max_length=10, null=True)),
                ('dotzapatos', models.CharField(blank=True, max_length=10, null=True)),
                ('estrato', models.CharField(blank=True, max_length=5, null=True)),
                ('numlibretamil', models.CharField(blank=True, max_length=10, null=True)),
                ('estadocontrato', models.SmallIntegerField(blank=True, null=True)),
                ('formatohv', models.CharField(blank=True, null=True)),
            ],
            options={
                'db_table': 'contratosemp',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Costos',
            fields=[
                ('nomcosto', models.CharField(blank=True, max_length=30, null=True)),
                ('idcosto', models.SmallIntegerField(primary_key=True, serialize=False)),
                ('grupocontable', models.CharField(blank=True, max_length=4, null=True)),
                ('suficosto', models.CharField(blank=True, max_length=2, null=True)),
            ],
            options={
                'db_table': 'costos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ModelosContratos',
            fields=[
                ('idmodelo', models.SmallIntegerField(primary_key=True, serialize=False)),
                ('nombremodelo', models.CharField(blank=True, max_length=255, null=True)),
                ('tipocontrato', models.CharField(blank=True, max_length=255, null=True)),
                ('textocontrato', models.CharField(blank=True, max_length=10485760, null=True)),
                ('estadomodelo', models.SmallIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'modelos_contratos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Sedes',
            fields=[
                ('nombresede', models.CharField(blank=True, max_length=40, null=True)),
                ('cajacompensacion', models.CharField(blank=True, max_length=60, null=True)),
                ('idsede', models.SmallIntegerField(primary_key=True, serialize=False)),
                ('codccf', models.CharField(blank=True, max_length=8, null=True)),
            ],
            options={
                'db_table': 'sedes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Subcostos',
            fields=[
                ('nomsubcosto', models.CharField(blank=True, max_length=30, null=True)),
                ('nomcosto', models.CharField(blank=True, max_length=30, null=True)),
                ('idsubcosto', models.SmallIntegerField(primary_key=True, serialize=False)),
                ('idcosto', models.SmallIntegerField(blank=True, null=True)),
                ('sufisubcosto', models.CharField(blank=True, max_length=2, null=True)),
            ],
            options={
                'db_table': 'subcostos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tipocontrato',
            fields=[
                ('idtipocontrato', models.IntegerField(primary_key=True, serialize=False)),
                ('tipocontrato', models.CharField(blank=True, max_length=255, null=True)),
                ('cod_dian', models.SmallIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tipocontrato',
                'managed': False,
            },
        ),
    ]
