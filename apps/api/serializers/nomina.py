from rest_framework import serializers
from apps.common.models import Crearnomina, Vacaciones, Liquidacion


class CrearnominaSerializer(serializers.ModelSerializer):
    tiponomina_nombre = serializers.SerializerMethodField()
    anoacumular_valor = serializers.SerializerMethodField()
    empresa_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Crearnomina
        fields = [
            'idnomina', 'nombrenomina', 'fechainicial',
            'fechafinal', 'fechapago', 'tiponomina',
            'tiponomina_nombre', 'mesacumular', 'anoacumular',
            'anoacumular_valor', 'estadonomina', 'diasnomina',
            'id_empresa', 'empresa_nombre', 'is_opened',
        ]
        read_only_fields = fields

    def get_tiponomina_nombre(self, obj):
        if obj.tiponomina:
            return obj.tiponomina.tipodenomina
        return None

    def get_anoacumular_valor(self, obj):
        if obj.anoacumular:
            return obj.anoacumular.ano
        return None

    def get_empresa_nombre(self, obj):
        if obj.id_empresa:
            return obj.id_empresa.nombreempresa
        return None


class VacacionesSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.SerializerMethodField()
    tipo_vacacion = serializers.SerializerMethodField()

    class Meta:
        model = Vacaciones
        fields = [
            'idvacaciones', 'idcontrato', 'empleado_nombre',
            'fechainicialvac', 'ultimodiavac', 'diascalendario',
            'diasvac', 'pagovac', 'basepago', 'cuentasabados',
            'tipovac', 'tipo_vacacion', 'idvacmaster',
            'perinicio', 'perfinal', 'fechapago',
        ]
        read_only_fields = fields

    def get_empleado_nombre(self, obj):
        try:
            emp = obj.idcontrato.idempleado
            return f"{emp.pnombre} {emp.papellido}"
        except Exception:
            return None

    def get_tipo_vacacion(self, obj):
        if obj.tipovac:
            return obj.tipovac.nombrevacaus
        return None


class LiquidacionSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.SerializerMethodField()
    empleado_id = serializers.SerializerMethodField()

    class Meta:
        model = Liquidacion
        fields = [
            'idliquidacion', 'idcontrato', 'empleado_id',
            'empleado_nombre', 'fechainiciocontrato',
            'fechafincontrato', 'salario', 'motivoretiro',
            'estadoliquidacion', 'diastrabajados',
            'diascesantias', 'diasprimas', 'diasvacaciones',
            'cesantias', 'prima', 'vacaciones', 'intereses',
            'totalliq', 'baseprima', 'basecesantias',
            'basevacaciones', 'diassusp', 'diassuspv',
            'indemnizacion',
        ]
        read_only_fields = fields

    def get_empleado_nombre(self, obj):
        try:
            emp = obj.idcontrato.idempleado
            return f"{emp.pnombre} {emp.papellido}"
        except Exception:
            return None

    def get_empleado_id(self, obj):
        try:
            return obj.idcontrato.idempleado.pk
        except Exception:
            return None
