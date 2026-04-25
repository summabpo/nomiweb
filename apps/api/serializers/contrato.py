from rest_framework import serializers
from apps.common.models import Contratos


class ContratosSerializer(serializers.ModelSerializer):
    eps_codigo = serializers.SerializerMethodField()
    afp_codigo = serializers.SerializerMethodField()
    ccf_codigo = serializers.SerializerMethodField()
    cesantias_codigo = serializers.SerializerMethodField()
    tipocontrato_nombre = serializers.SerializerMethodField()
    tiponomina_nombre = serializers.SerializerMethodField()
    tiposalario_nombre = serializers.SerializerMethodField()
    tipocotizante_cod = serializers.SerializerMethodField()
    subtipocotizante_cod = serializers.SerializerMethodField()
    cargo_nombre = serializers.SerializerMethodField()
    banco_cod = serializers.SerializerMethodField()
    ciudad_contratacion_cod = serializers.SerializerMethodField()
    empleado_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Contratos
        fields = [
            'idcontrato',
            'idempleado', 'empleado_nombre',
            'id_empresa',
            'cargo', 'cargo_nombre',
            'fechainiciocontrato', 'fechafincontrato',
            'tipocontrato', 'tipocontrato_nombre',
            'tiponomina', 'tiponomina_nombre',
            'bancocuenta', 'banco_cod',
            'cuentanomina', 'tipocuentanomina',
            'centrotrabajo',
            'ciudadcontratacion', 'ciudad_contratacion_cod',
            'estadocontrato', 'estadoliquidacion', 'estadosegsocial',
            'salario', 'tiposalario', 'tiposalario_nombre',
            'salariovariable',
            'tipocotizante', 'tipocotizante_cod',
            'subtipocotizante', 'subtipocotizante_cod',
            'codeps', 'eps_codigo',
            'codafp', 'afp_codigo',
            'codccf', 'ccf_codigo',
            'fondocesantias', 'cesantias_codigo',
            'auxiliotransporte', 'jornada',
            'idcosto', 'idsubcosto', 'idsede',
            'formapago', 'metodoretefuente',
            'porcentajeretefuente', 'valordeduciblevivienda',
            'saludretefuente', 'pensionado',
            'dependientes', 'valordeduciblemedicina',
            'riesgo_pension',
            'old_idcontrato',
        ]

    def get_eps_codigo(self, obj):
        if obj.codeps:
            return obj.codeps.codigo
        return None

    def get_afp_codigo(self, obj):
        if obj.codafp:
            return obj.codafp.codigo
        return None

    def get_ccf_codigo(self, obj):
        if obj.codccf:
            return obj.codccf.codigo
        return None

    def get_cesantias_codigo(self, obj):
        if obj.fondocesantias:
            return obj.fondocesantias.codigo
        return None

    def get_tipocontrato_nombre(self, obj):
        if obj.tipocontrato:
            return obj.tipocontrato.tipocontrato
        return None

    def get_tiponomina_nombre(self, obj):
        if obj.tiponomina:
            return obj.tiponomina.tipodenomina
        return None

    def get_tiposalario_nombre(self, obj):
        if obj.tiposalario:
            return obj.tiposalario.tiposalario
        return None

    def get_tipocotizante_cod(self, obj):
        if obj.tipocotizante:
            return obj.tipocotizante.tipocotizante
        return None

    def get_subtipocotizante_cod(self, obj):
        if obj.subtipocotizante:
            return obj.subtipocotizante.subtipocotizante
        return None

    def get_cargo_nombre(self, obj):
        if obj.cargo:
            return obj.cargo.nombrecargo
        return None

    def get_banco_cod(self, obj):
        if obj.bancocuenta:
            return obj.bancocuenta.codbanco
        return None

    def get_ciudad_contratacion_cod(self, obj):
        if obj.ciudadcontratacion:
            return obj.ciudadcontratacion.codciudad
        return None

    def get_empleado_nombre(self, obj):
        if obj.idempleado:
            emp = obj.idempleado
            return f"{emp.pnombre} {emp.papellido}"
        return None
